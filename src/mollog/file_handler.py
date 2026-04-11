import time
from pathlib import Path

from mollog.handler import Handler
from mollog.level import Level
from mollog.record import LogRecord


class FileHandler(Handler):
    """Append log records to a file."""

    def __init__(self, path: str | Path, level: Level = Level.TRACE) -> None:
        super().__init__(level)
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self._path, "a", encoding="utf-8")  # noqa: SIM115

    def emit(self, record: LogRecord) -> None:
        line = self._formatter.format(record)
        self._file.write(line + "\n")
        self._file.flush()

    def close(self) -> None:
        self._file.close()


class RotatingFileHandler(Handler):
    """Rotate log file when it exceeds *max_bytes*."""

    def __init__(
        self,
        path: str | Path,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        level: Level = Level.TRACE,
    ) -> None:
        super().__init__(level)
        if max_bytes <= 0:
            raise ValueError("max_bytes must be greater than 0")
        if backup_count < 0:
            raise ValueError("backup_count must be greater than or equal to 0")
        self._path = Path(path)
        self._max_bytes = max_bytes
        self._backup_count = backup_count
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self._path, "a", encoding="utf-8")  # noqa: SIM115

    def emit(self, record: LogRecord) -> None:
        line = self._formatter.format(record)
        self._file.write(line + "\n")
        self._file.flush()
        if self._path.stat().st_size >= self._max_bytes:
            self._rotate()

    def _rotate(self) -> None:
        self._file.close()
        if self._backup_count == 0:
            self._path.unlink(missing_ok=True)
            self._file = open(self._path, "a", encoding="utf-8")  # noqa: SIM115
            return
        # shift existing backups
        for i in range(self._backup_count - 1, 0, -1):
            src = self._path.with_suffix(f"{self._path.suffix}.{i}")
            dst = self._path.with_suffix(f"{self._path.suffix}.{i + 1}")
            if src.exists():
                src.rename(dst)
        # rename current to .1
        dst = self._path.with_suffix(f"{self._path.suffix}.1")
        self._path.rename(dst)
        # delete overflow backup
        overflow = self._path.with_suffix(f"{self._path.suffix}.{self._backup_count + 1}")
        if overflow.exists():
            overflow.unlink()
        self._file = open(self._path, "a", encoding="utf-8")  # noqa: SIM115

    def close(self) -> None:
        self._file.close()


class TimedRotatingFileHandler(Handler):
    """Rotate log file based on a time interval."""

    _UNITS: dict[str, int] = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
    }

    def __init__(
        self,
        path: str | Path,
        when: str = "h",
        interval: int = 1,
        backup_count: int = 5,
        level: Level = Level.TRACE,
    ) -> None:
        super().__init__(level)
        if interval <= 0:
            raise ValueError("interval must be greater than 0")
        if backup_count < 0:
            raise ValueError("backup_count must be greater than or equal to 0")
        self._path = Path(path)
        if when not in self._UNITS:
            raise ValueError(f"Invalid 'when' value: {when!r}. Use one of {list(self._UNITS)}")
        self._interval_seconds = self._UNITS[when] * interval
        self._backup_count = backup_count
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self._path, "a", encoding="utf-8")  # noqa: SIM115
        self._next_rotation = time.monotonic() + self._interval_seconds

    def emit(self, record: LogRecord) -> None:
        line = self._formatter.format(record)
        self._file.write(line + "\n")
        self._file.flush()
        if time.monotonic() >= self._next_rotation:
            self._rotate()

    def _rotate(self) -> None:
        self._file.close()
        if self._backup_count == 0:
            self._path.unlink(missing_ok=True)
            self._file = open(self._path, "a", encoding="utf-8")  # noqa: SIM115
            self._next_rotation = time.monotonic() + self._interval_seconds
            return
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        rotated = self._path.with_suffix(f"{self._path.suffix}.{timestamp}")
        self._path.rename(rotated)
        self._file = open(self._path, "a", encoding="utf-8")  # noqa: SIM115
        self._next_rotation = time.monotonic() + self._interval_seconds
        self._cleanup_old_backups()

    def _cleanup_old_backups(self) -> None:
        pattern = f"{self._path.name}.*"
        backups = sorted(self._path.parent.glob(pattern), key=lambda p: p.stat().st_mtime)
        while len(backups) > self._backup_count:
            backups.pop(0).unlink()

    def close(self) -> None:
        self._file.close()
