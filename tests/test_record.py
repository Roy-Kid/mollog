from datetime import datetime, timezone

import pytest

from mollog.level import Level
from mollog.record import LogRecord


def test_record_creation():
    r = LogRecord(level=Level.INFO, message="hello", logger_name="test")
    assert r.level == Level.INFO
    assert r.message == "hello"
    assert r.logger_name == "test"
    assert isinstance(r.timestamp, datetime)
    assert r.extra == {}


def test_record_with_extra():
    r = LogRecord(level=Level.DEBUG, message="x", logger_name="a", extra={"k": "v"})
    assert r.extra["k"] == "v"


def test_record_with_exception_and_stack():
    r = LogRecord(
        level=Level.ERROR,
        message="boom",
        logger_name="a",
        exception="Traceback...",
        stack_info="frame a\nframe b",
    )
    assert r.exception == "Traceback..."
    assert "frame a" in r.stack_info


def test_record_immutability():
    r = LogRecord(level=Level.INFO, message="hi", logger_name="test")
    with pytest.raises(AttributeError):
        r.message = "changed"  # type: ignore[misc]


def test_record_timestamp_is_utc():
    r = LogRecord(level=Level.INFO, message="t", logger_name="t")
    assert r.timestamp.tzinfo == timezone.utc
