from abc import ABC, abstractmethod

from mollog.level import Level
from mollog.record import LogRecord


class Filter(ABC):
    """Base class for log record filters.

    Return ``True`` from :meth:`filter` to let the record pass.
    """

    @abstractmethod
    def filter(self, record: LogRecord) -> bool: ...


class LevelFilter(Filter):
    """Pass only records within a level range."""

    def __init__(
        self,
        min_level: Level | None = None,
        max_level: Level | None = None,
    ) -> None:
        self._min = min_level
        self._max = max_level

    def filter(self, record: LogRecord) -> bool:
        if self._min is not None and record.level < self._min:
            return False
        if self._max is not None and record.level > self._max:
            return False
        return True
