from __future__ import annotations

import sys
import threading
import traceback
from types import TracebackType
from typing import Any

from mollog._context import Context
from mollog._handler import Handler
from mollog._level import Level
from mollog._record import LogRecord

ExcInfo = tuple[type[BaseException], BaseException, TracebackType | None]
ExcInfoArg = bool | BaseException | ExcInfo | None


class Logger:
    """Named logger that dispatches records to handlers."""

    def __init__(
        self,
        name: str,
        level: Level = Level.TRACE,
        *,
        propagate: bool = True,
        bound_extra: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.level = level
        self.propagate = propagate
        self.handlers: list[Handler] = []
        self.parent: Logger | None = None
        self._lock = threading.RLock()
        self._bound_extra: dict[str, Any] = dict(bound_extra) if bound_extra else {}

    def add_handler(self, handler: Handler) -> None:
        with self._lock:
            self.handlers.append(handler)

    def remove_handler(self, handler: Handler) -> None:
        with self._lock:
            self.handlers.remove(handler)

    def clear_handlers(self, *, close: bool = False) -> None:
        with self._lock:
            handlers = tuple(self.handlers)
            self.handlers.clear()

        if close:
            for handler in handlers:
                handler.close()

    def is_enabled_for(self, level: Level) -> bool:
        return level >= self.level

    def _merged_extra(self, call_extra: dict[str, Any] | None) -> dict[str, Any]:
        merged = Context.get()
        if self._bound_extra:
            merged.update(self._bound_extra)
        if call_extra:
            merged.update(call_extra)
        return merged

    def _log(
        self,
        level: Level,
        message: str,
        extra: dict[str, Any] | None = None,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
    ) -> None:
        if not self.is_enabled_for(level):
            return
        record = LogRecord(
            level=level,
            message=message,
            logger_name=self.name,
            extra=self._merged_extra(extra),
            exception=_format_exception(exc_info),
            stack_info=_format_stack_info() if stack_info else None,
        )
        self._dispatch(record)

    def _dispatch(self, record: LogRecord) -> None:
        with self._lock:
            handlers = tuple(self.handlers)
            parent = self.parent
            propagate = self.propagate

        for h in handlers:
            h.handle(record)
        if propagate and parent is not None:
            parent._dispatch(record)

    def trace(
        self,
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        self._log(Level.TRACE, message, extra or None, exc_info=exc_info, stack_info=stack_info)

    def debug(
        self,
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        self._log(Level.DEBUG, message, extra or None, exc_info=exc_info, stack_info=stack_info)

    def info(
        self,
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        self._log(Level.INFO, message, extra or None, exc_info=exc_info, stack_info=stack_info)

    def warning(
        self,
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        self._log(Level.WARNING, message, extra or None, exc_info=exc_info, stack_info=stack_info)

    def error(
        self,
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        self._log(Level.ERROR, message, extra or None, exc_info=exc_info, stack_info=stack_info)

    def critical(
        self,
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        self._log(Level.CRITICAL, message, extra or None, exc_info=exc_info, stack_info=stack_info)

    def exception(self, message: str, **extra: Any) -> None:
        self._log(Level.ERROR, message, extra or None, exc_info=True)

    def fire(
        self,
        message: str,
        *,
        level: Level | str | int = Level.INFO,
        **extra: Any,
    ) -> None:
        """Dispatch an event *only* to attached :class:`LogfireHandler` instances.

        Walks the logger chain (respecting ``propagate``) and calls every
        ``LogfireHandler`` it finds; records never reach other handler
        types via this path, so ``logger.fire`` stays a dedicated logfire
        channel. Raises :class:`RuntimeError` if no ``LogfireHandler`` is
        attached.
        """

        from mollog._logfire import LogfireHandler

        resolved = Level.coerce(level)
        record = LogRecord(
            level=resolved,
            message=message,
            logger_name=self.name,
            extra=self._merged_extra(extra or None),
        )

        delivered = 0
        current: Logger | None = self
        while current is not None:
            with current._lock:
                handlers = tuple(current.handlers)
                parent = current.parent
                propagate = current.propagate
            for handler in handlers:
                if isinstance(handler, LogfireHandler):
                    handler.handle(record)
                    delivered += 1
            if not propagate:
                break
            current = parent

        if delivered == 0:
            raise RuntimeError(
                "logger.fire() needs at least one LogfireHandler attached; "
                "call logger.add_handler(LogfireHandler()) first"
            )

    def bind(self, **extra: Any) -> Logger:
        """Return a view of this logger with additional persistent fields.

        The returned object is a :class:`Logger` that shares the underlying
        handler list and hierarchy with ``self`` and carries ``**extra``
        merged on top of any already-bound fields. It is not registered
        with :class:`LoggerManager`.
        """

        merged = {**self._bound_extra, **extra}
        view = Logger.__new__(Logger)
        view.name = self.name
        view.level = self.level
        view.propagate = self.propagate
        view.handlers = self.handlers
        view.parent = self.parent
        view._lock = self._lock
        view._bound_extra = merged
        return view

    def close(self) -> None:
        self.clear_handlers(close=True)


def _format_exception(exc_info: ExcInfoArg) -> str | None:
    resolved = _resolve_exc_info(exc_info)
    if resolved is None:
        return None
    return "".join(traceback.format_exception(*resolved)).rstrip()


def _resolve_exc_info(exc_info: ExcInfoArg) -> ExcInfo | None:
    if not exc_info:
        return None
    if exc_info is True:
        current = sys.exc_info()
        if current[0] is None or current[1] is None:
            return None
        return current
    if isinstance(exc_info, BaseException):
        return (type(exc_info), exc_info, exc_info.__traceback__)
    return exc_info


def _format_stack_info() -> str:
    return "".join(traceback.format_stack()[:-2]).rstrip()
