import time
from pathlib import Path

import pytest

from mollog.file_handler import FileHandler, RotatingFileHandler, TimedRotatingFileHandler
from mollog.level import Level
from mollog.record import LogRecord


def _rec(msg: str = "line") -> LogRecord:
    return LogRecord(level=Level.INFO, message=msg, logger_name="t")


class TestFileHandler:
    def test_append_to_file(self, tmp_path: Path):
        p = tmp_path / "app.log"
        h = FileHandler(p)
        h.handle(_rec("first"))
        h.handle(_rec("second"))
        h.close()
        text = p.read_text()
        assert "first" in text
        assert "second" in text


class TestRotatingFileHandler:
    def test_rotation(self, tmp_path: Path):
        p = tmp_path / "rot.log"
        h = RotatingFileHandler(p, max_bytes=50, backup_count=2)
        for i in range(20):
            h.handle(_rec(f"msg-{i:04d}"))
        h.close()
        # main file should exist
        assert p.exists()
        # at least one backup should have been created
        backups = list(tmp_path.glob("rot.log.*"))
        assert len(backups) >= 1

    def test_rotation_without_backups_discards_old_file(self, tmp_path: Path):
        p = tmp_path / "rot.log"
        h = RotatingFileHandler(p, max_bytes=50, backup_count=0)
        for i in range(20):
            h.handle(_rec(f"msg-{i:04d}"))
        h.close()

        assert p.exists()
        assert list(tmp_path.glob("rot.log.*")) == []

    def test_invalid_rotation_configuration(self, tmp_path: Path):
        p = tmp_path / "rot.log"
        with pytest.raises(ValueError):
            RotatingFileHandler(p, max_bytes=0)
        with pytest.raises(ValueError):
            RotatingFileHandler(p, backup_count=-1)


class TestTimedRotatingFileHandler:
    def test_rotation(self, tmp_path: Path):
        p = tmp_path / "timed.log"
        h = TimedRotatingFileHandler(p, when="s", interval=1, backup_count=2)
        h._next_rotation = time.monotonic()
        h.handle(_rec("tick"))
        h.close()

        assert p.exists()
        backups = list(tmp_path.glob("timed.log.*"))
        assert len(backups) == 1

    def test_rotation_without_backups_discards_old_file(self, tmp_path: Path):
        p = tmp_path / "timed.log"
        h = TimedRotatingFileHandler(p, when="s", interval=1, backup_count=0)
        h._next_rotation = time.monotonic()
        h.handle(_rec("tick"))
        h.close()

        assert p.exists()
        assert list(tmp_path.glob("timed.log.*")) == []

    def test_invalid_timed_rotation_configuration(self, tmp_path: Path):
        p = tmp_path / "timed.log"
        with pytest.raises(ValueError):
            TimedRotatingFileHandler(p, interval=0)
        with pytest.raises(ValueError):
            TimedRotatingFileHandler(p, backup_count=-1)
