from __future__ import annotations

import sys
import threading
import traceback
from types import TracebackType
from typing import Any

from mollog.context import get_context
from mollog.handler import Handler
from mollog.level import Level
from mollog.record import LogRecord

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
    ) -> None:
        self.name = name
        self.level = level
        self.propagate = propagate
        self.handlers: list[Handler] = []
        self.parent: Logger | None = None
        self._lock = threading.RLock()

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
        merged_extra = get_context()
        if extra:
            merged_extra.update(extra)
        record = LogRecord(
            level=level,
            message=message,
            logger_name=self.name,
            extra=merged_extra,
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

    def bind(self, **extra: Any) -> BoundLogger:
        return BoundLogger(self, extra)

    def close(self) -> None:
        self.clear_handlers(close=True)


class BoundLogger:
    """Logger wrapper that merges pre-bound extra fields into every record."""

    def __init__(self, logger: Logger, extra: dict[str, Any]) -> None:
        self._logger = logger
        self._extra = extra

    @property
    def name(self) -> str:
        return self._logger.name

    def _merge(self, extra: dict[str, Any] | None) -> dict[str, Any]:
        if extra:
            return {**self._extra, **extra}
        return dict(self._extra)

    def trace(
        self,
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        self._logger._log(
            Level.TRACE,
            message,
            self._merge(extra or None),
            exc_info=exc_info,
            stack_info=stack_info,
        )

    def debug(
        self,
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        self._logger._log(
            Level.DEBUG,
            message,
            self._merge(extra or None),
            exc_info=exc_info,
            stack_info=stack_info,
        )

    def info(
        self,
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        self._logger._log(
            Level.INFO,
            message,
            self._merge(extra or None),
            exc_info=exc_info,
            stack_info=stack_info,
        )

    def warning(
        self,
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        self._logger._log(
            Level.WARNING,
            message,
            self._merge(extra or None),
            exc_info=exc_info,
            stack_info=stack_info,
        )

    def error(
        self,
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        self._logger._log(
            Level.ERROR,
            message,
            self._merge(extra or None),
            exc_info=exc_info,
            stack_info=stack_info,
        )

    def critical(
        self,
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        self._logger._log(
            Level.CRITICAL,
            message,
            self._merge(extra or None),
            exc_info=exc_info,
            stack_info=stack_info,
        )

    def exception(self, message: str, **extra: Any) -> None:
        self._logger._log(Level.ERROR, message, self._merge(extra or None), exc_info=True)

    def bind(self, **extra: Any) -> BoundLogger:
        return BoundLogger(self._logger, {**self._extra, **extra})


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
