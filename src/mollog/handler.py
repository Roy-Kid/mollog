import sys
import threading
from abc import ABC, abstractmethod
from typing import IO

from mollog.filter import Filter
from mollog.formatter import Formatter, TextFormatter
from mollog.level import Level
from mollog.record import LogRecord


class Handler(ABC):
    """Base class for log handlers."""

    def __init__(self, level: Level = Level.TRACE) -> None:
        self._level = level
        self._formatter: Formatter = TextFormatter()
        self._filters: list[Filter] = []
        self._lock = threading.Lock()

    @property
    def level(self) -> Level:
        return self._level

    def set_level(self, level: Level) -> None:
        self._level = level

    def set_formatter(self, formatter: Formatter) -> None:
        self._formatter = formatter

    def add_filter(self, f: Filter) -> None:
        self._filters.append(f)

    def remove_filter(self, f: Filter) -> None:
        self._filters.remove(f)

    def clear_filters(self) -> None:
        self._filters.clear()

    def handle(self, record: LogRecord) -> None:
        if record.level < self._level:
            return
        for f in self._filters:
            if not f.filter(record):
                return
        with self._lock:
            self.emit(record)

    @abstractmethod
    def emit(self, record: LogRecord) -> None: ...

    def close(self) -> None:
        pass

    def __enter__(self) -> "Handler":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class StreamHandler(Handler):
    """Write log records to a stream (default: stderr)."""

    def __init__(
        self,
        stream: IO[str] | None = None,
        level: Level = Level.TRACE,
    ) -> None:
        super().__init__(level)
        self._stream: IO[str] = stream or sys.stderr

    def emit(self, record: LogRecord) -> None:
        line = self._formatter.format(record)
        self._stream.write(line + "\n")
        self._stream.flush()


class NullHandler(Handler):
    """Discard all records."""

    def emit(self, record: LogRecord) -> None:
        pass
