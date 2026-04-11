from __future__ import annotations

import sys
import threading
from collections.abc import Iterable
from typing import IO

from mollog.context import clear_context
from mollog.formatter import Formatter, TextFormatter
from mollog.handler import Handler, StreamHandler
from mollog.level import Level
from mollog.logger import Logger


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
        replace: bool = True,
        stream: IO[str] | None = None,
    ) -> Logger:
        """Configure the root logger for library or application use."""

        resolved_level = Level.coerce(level)
        with self._state_lock:
            root = self._root
            root.level = resolved_level

            if replace:
                root.clear_handlers(close=True)

            normalized_handlers = list(handlers or [])
            if not normalized_handlers:
                if replace or not root.handlers:
                    default_handler = StreamHandler(
                        stream=stream or sys.stderr,
                        level=resolved_level,
                    )
                    default_handler.set_formatter(formatter or TextFormatter())
                    normalized_handlers.append(default_handler)
            elif formatter is not None:
                for handler in normalized_handlers:
                    handler.set_formatter(formatter)

            for handler in normalized_handlers:
                root.add_handler(handler)

            self._configured = True
            return root

    def shutdown(self) -> None:
        """Close all registered handlers and clear runtime state."""

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
        clear_context()

    def _reset(self) -> None:
        """Reset state (for testing only)."""
        with self._state_lock:
            self._loggers.clear()
            self._root = Logger("", Level.INFO)
            self._loggers[""] = self._root
            self._configured = False


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
    replace: bool = True,
    stream: IO[str] | None = None,
) -> Logger:
    """Configure and return the root logger."""

    return LoggerManager().configure(
        level=level,
        handlers=handlers,
        formatter=formatter,
        replace=replace,
        stream=stream,
    )


def shutdown() -> None:
    """Close all configured handlers and clear context-local state."""

    LoggerManager().shutdown()
