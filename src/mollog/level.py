from enum import IntEnum
from typing import Self


class Level(IntEnum):
    """Log severity levels in ascending order."""

    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    def __str__(self) -> str:
        return self.name

    @classmethod
    def coerce(cls, value: int | str | Self) -> Self:
        """Convert an int, enum value, or level name into a ``Level``."""

        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            normalized = value.strip().upper()
            try:
                return cls[normalized]
            except KeyError as exc:
                raise ValueError(f"Unknown log level: {value!r}") from exc
        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError(f"Unknown log level: {value!r}") from exc
