import json
from datetime import datetime, timezone

from mollog.formatter import JSONFormatter, TextFormatter
from mollog.level import Level
from mollog.record import LogRecord


def _make_record(**kw) -> LogRecord:
    defaults = {
        "level": Level.INFO,
        "message": "hello",
        "logger_name": "test",
        "timestamp": datetime(2025, 1, 15, 12, 0, 0, 123456, tzinfo=timezone.utc),
    }
    defaults.update(kw)
    return LogRecord(**defaults)


class TestTextFormatter:
    def test_default_format(self):
        fmt = TextFormatter()
        out = fmt.format(_make_record())
        assert "INFO" in out
        assert "test" in out
        assert "hello" in out
        assert "2025-01-15" in out

    def test_extra_fields_appended(self):
        fmt = TextFormatter()
        out = fmt.format(_make_record(extra={"request_id": "abc"}))
        assert "request_id=abc" in out

    def test_custom_template(self):
        fmt = TextFormatter(template="{level} - {message}")
        out = fmt.format(_make_record())
        assert out == "INFO - hello"

    def test_reserved_extra_fields_are_renamed(self):
        fmt = TextFormatter(template="{level} - {extra_level}")
        out = fmt.format(_make_record(extra={"level": "user-supplied"}))
        assert out == "INFO - user-supplied"

    def test_exception_and_stack_appended(self):
        fmt = TextFormatter()
        out = fmt.format(_make_record(exception="ValueError: boom", stack_info="frame one"))
        assert "ValueError: boom" in out
        assert "Stack (most recent call last):" in out
        assert "frame one" in out


class TestJSONFormatter:
    def test_valid_json(self):
        fmt = JSONFormatter()
        out = fmt.format(_make_record())
        data = json.loads(out)
        assert data["message"] == "hello"
        assert data["level"] == "INFO"
        assert data["logger_name"] == "test"

    def test_extra_merged(self):
        fmt = JSONFormatter()
        out = fmt.format(_make_record(extra={"user": "bob"}))
        data = json.loads(out)
        assert data["user"] == "bob"

    def test_single_line(self):
        fmt = JSONFormatter()
        out = fmt.format(_make_record())
        assert "\n" not in out

    def test_reserved_extra_fields_do_not_override_core_fields(self):
        fmt = JSONFormatter()
        out = fmt.format(_make_record(extra={"message": "shadow", "level": "DEBUG"}))
        data = json.loads(out)
        assert data["message"] == "hello"
        assert data["level"] == "INFO"
        assert data["extra_message"] == "shadow"
        assert data["extra_level"] == "DEBUG"

    def test_exception_and_stack_are_serialized(self):
        fmt = JSONFormatter()
        out = fmt.format(_make_record(exception="ValueError: boom", stack_info="frame one"))
        data = json.loads(out)
        assert data["exception"] == "ValueError: boom"
        assert data["stack_info"] == "frame one"
