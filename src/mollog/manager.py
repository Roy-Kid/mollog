from __future__ import annotations

import atexit
import sys
import threading
from collections.abc import Iterable
from pathlib import Path
from typing import IO, Any

from mollog.context import clear_context
from mollog.file_handler import FileHandler
from mollog.formatter import Formatter, StdlibStyleFormatter, TextFormatter
from mollog.handler import Handler, StreamHandler
from mollog.level import Level
from mollog.logger import ExcInfoArg, Logger
from mollog.stdlib_bridge import capture_stdlib_logging, release_stdlib_logging


class LoggerManager:
    """Singleton registry of loggers with hierarchy support."""

    _instance: LoggerManager | None = None
    _init_lock = threading.Lock()

    _loggers: dict[str, Logger]
    _root: Logger
    _configured: bool
    _state_lock: threading.RLock

    def __new__(cls) -> LoggerManager:
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._loggers = {}
                    inst._root = Logger("", Level.INFO)
                    inst._loggers[""] = inst._root
                    inst._configured = False
                    inst._state_lock = threading.RLock()
                    cls._instance = inst
        return cls._instance

    @property
    def root(self) -> Logger:
        return self._root

    def get_logger(self, name: str = "") -> Logger:
        with self._state_lock:
            if name in self._loggers:
                return self._loggers[name]

            logger = Logger(name)
            self._loggers[name] = logger

            parts = name.rsplit(".", 1)
            if len(parts) > 1:
                parent_name = parts[0]
                logger.parent = self.get_logger(parent_name)
            else:
                logger.parent = self._root

            return logger

    def ensure_default_handler(self) -> None:
        """Add a default StreamHandler to root if it has none."""
        with self._state_lock:
            if not self._configured and not self._root.handlers:
                handler = StreamHandler(stream=sys.stderr, level=Level.INFO)
                handler.set_formatter(TextFormatter())
                self._root.add_handler(handler)
                self._configured = True

    def configure(
        self,
        *,
        level: Level | str | int = Level.INFO,
        handlers: Iterable[Handler] | None = None,
        formatter: Formatter | None = None,
        format: str | None = None,
        datefmt: str | None = None,
        replace: bool = True,
        stream: IO[str] | None = None,
        filename: str | Path | None = None,
        filemode: str = "a",
        file_level: Level | str | int | None = None,
        file_formatter: Formatter | None = None,
        encoding: str = "utf-8",
        capture_stdlib: bool = True,
    ) -> Logger:
        """Configure the root logger for library or application use.

        Parameters mirror :func:`logging.basicConfig` where sensible. The
        important dual-destination case — ``stream + filename`` — attaches
        *both* a :class:`StreamHandler` and a :class:`FileHandler` to the
        root logger so records show up on the terminal **and** in the file.

        Precedence rules:

        * If *handlers* is given, it fully overrides *stream* / *filename*:
          the caller is taking manual control of the handler list. A
          shared *formatter* (if given) is still applied to each handler.
        * Otherwise a :class:`StreamHandler` is always added (on *stream*
          or ``sys.stderr``). If *filename* is also provided, a
          :class:`FileHandler` is added alongside it.
        * *file_level* / *file_formatter* let the file sink diverge from
          the console (e.g. DEBUG to file, INFO to terminal).
        * *format* accepts a stdlib :func:`logging.basicConfig`-style
          format string (``"%(asctime)s %(levelname)s %(name)s %(message)s"``)
          and is rendered through :class:`StdlibStyleFormatter`. Mutually
          exclusive with *formatter* — pass one or the other.
        * *capture_stdlib* (default ``True``) installs a
          :class:`StdlibBridgeHandler` on stdlib's root logger so that
          third-party libraries which emit through :mod:`logging`
          (httpx, urllib3, …) flow through mollog's hierarchy. Pass
          ``False`` to leave stdlib alone.
        """

        if formatter is not None and format is not None:
            raise ValueError("pass either `formatter` or `format`, not both")

        resolved_level = Level.coerce(level)
        resolved_file_level = Level.coerce(file_level) if file_level is not None else resolved_level

        if formatter is None and format is not None:
            formatter = StdlibStyleFormatter(format, datefmt=datefmt)

        with self._state_lock:
            root = self._root
            root.level = resolved_level

            if replace:
                root.clear_handlers(close=True)

            provided = list(handlers or [])
            if provided:
                if formatter is not None:
                    for handler in provided:
                        handler.set_formatter(formatter)
                for handler in provided:
                    root.add_handler(handler)
            elif replace or not root.handlers:
                shared_formatter = formatter or TextFormatter()

                stream_handler = StreamHandler(
                    stream=stream or sys.stderr,
                    level=resolved_level,
                )
                stream_handler.set_formatter(shared_formatter)
                root.add_handler(stream_handler)

                if filename is not None:
                    file_handler = FileHandler(
                        Path(filename),
                        mode=filemode,
                        encoding=encoding,
                        level=resolved_file_level,
                    )
                    file_handler.set_formatter(file_formatter or shared_formatter)
                    root.add_handler(file_handler)

            self._configured = True

        if capture_stdlib:
            capture_stdlib_logging(replace=replace)
        elif replace:
            release_stdlib_logging()

        return root

    def shutdown(self) -> None:
        """Close all registered handlers and clear runtime state.

        Idempotent: safe to call multiple times. Registered as an
        :func:`atexit` hook so even ad-hoc loggers don't leak handles
        on normal interpreter exit. Also removes any
        :class:`StdlibBridgeHandler` installed on stdlib's root logger.
        """

        with self._state_lock:
            closed: set[int] = set()
            for logger in self._loggers.values():
                handlers = tuple(logger.handlers)
                logger.clear_handlers(close=False)
                for handler in handlers:
                    ident = id(handler)
                    if ident in closed:
                        continue
                    handler.close()
                    closed.add(ident)
            self._configured = False
        release_stdlib_logging()
        clear_context()

    def close_logger(self, name: str) -> None:
        """Drop ``name`` from the registry and close its handlers.

        Idempotent: closing an unknown name is a no-op. Children of
        ``name`` (in the dotted hierarchy) are unaffected — only the
        named logger is released. After this call,
        ``get_logger(name)`` returns a fresh, handler-less Logger.

        Use this when the lifetime of a logger is tied to an external
        identifier (a session id, a request id, an experiment id) and
        the caller knows the identifier is finished. For scoped usage
        within a function, use :class:`Logger` as a context manager
        instead.
        """

        with self._state_lock:
            logger = self._loggers.pop(name, None)
        if logger is not None:
            logger.close()

    def _reset(self) -> None:
        """Reset state (for testing only)."""
        with self._state_lock:
            self._loggers.clear()
            self._root = Logger("", Level.INFO)
            self._loggers[""] = self._root
            self._configured = False
        release_stdlib_logging()


def get_logger(name: str = "") -> Logger:
    """Get or create a logger by name.

    On first call, attaches a default StreamHandler to the root logger
    if no handlers are configured.
    """
    mgr = LoggerManager()
    mgr.ensure_default_handler()
    return mgr.get_logger(name)


def configure(
    *,
    level: Level | str | int = Level.INFO,
    handlers: Iterable[Handler] | None = None,
    formatter: Formatter | None = None,
    format: str | None = None,
    datefmt: str | None = None,
    replace: bool = True,
    stream: IO[str] | None = None,
    filename: str | Path | None = None,
    filemode: str = "a",
    file_level: Level | str | int | None = None,
    file_formatter: Formatter | None = None,
    encoding: str = "utf-8",
    capture_stdlib: bool = True,
) -> Logger:
    """Configure and return the root logger.

    See :meth:`LoggerManager.configure` for the full parameter reference.
    The short version: pass *filename* to also mirror records into a file
    alongside the terminal stream; pass *format* (stdlib ``%(asctime)s``
    style) instead of *formatter* if you're migrating from
    :func:`logging.basicConfig`. *capture_stdlib* (default ``True``)
    routes stdlib :mod:`logging` records through mollog so libraries
    like httpx are governed by the same hierarchy.
    """

    return LoggerManager().configure(
        level=level,
        handlers=handlers,
        formatter=formatter,
        format=format,
        datefmt=datefmt,
        replace=replace,
        stream=stream,
        filename=filename,
        filemode=filemode,
        file_level=file_level,
        file_formatter=file_formatter,
        encoding=encoding,
        capture_stdlib=capture_stdlib,
    )


def shutdown() -> None:
    """Close all configured handlers and clear context-local state."""

    LoggerManager().shutdown()


def close_logger(name: str) -> None:
    """Module-level convenience for :meth:`LoggerManager.close_logger`."""

    LoggerManager().close_logger(name)


def set_level(level: Level | str | int) -> None:
    """Set the root logger's minimum level (mollog and stdlib bridge)."""

    get_logger("").set_level(level)


def trace(
    message: str,
    *,
    exc_info: ExcInfoArg = None,
    stack_info: bool = False,
    **extra: Any,
) -> None:
    get_logger("").trace(message, exc_info=exc_info, stack_info=stack_info, **extra)


def debug(
    message: str,
    *,
    exc_info: ExcInfoArg = None,
    stack_info: bool = False,
    **extra: Any,
) -> None:
    get_logger("").debug(message, exc_info=exc_info, stack_info=stack_info, **extra)


def info(
    message: str,
    *,
    exc_info: ExcInfoArg = None,
    stack_info: bool = False,
    **extra: Any,
) -> None:
    get_logger("").info(message, exc_info=exc_info, stack_info=stack_info, **extra)


def warning(
    message: str,
    *,
    exc_info: ExcInfoArg = None,
    stack_info: bool = False,
    **extra: Any,
) -> None:
    get_logger("").warning(message, exc_info=exc_info, stack_info=stack_info, **extra)


def error(
    message: str,
    *,
    exc_info: ExcInfoArg = None,
    stack_info: bool = False,
    **extra: Any,
) -> None:
    get_logger("").error(message, exc_info=exc_info, stack_info=stack_info, **extra)


def critical(
    message: str,
    *,
    exc_info: ExcInfoArg = None,
    stack_info: bool = False,
    **extra: Any,
) -> None:
    get_logger("").critical(message, exc_info=exc_info, stack_info=stack_info, **extra)


def exception(message: str, **extra: Any) -> None:
    get_logger("").exception(message, **extra)


# Register the singleton's shutdown as an interpreter-exit hook so
# ad-hoc loggers don't leak file handles on normal exit. ``shutdown`` is
# idempotent, so an explicit user call followed by atexit firing is
# safe. Mirrors the contract of stdlib ``logging`` (which registers an
# equivalent ``atexit`` hook on first import).
atexit.register(LoggerManager().shutdown)
