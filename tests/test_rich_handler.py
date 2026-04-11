# ruff: noqa: E402

import io

import pytest

rich = pytest.importorskip("rich")

from rich.console import Console

from mollog import RichHandler
from mollog.formatter import JSONFormatter
from mollog.level import Level
from mollog.record import LogRecord


def _rec(
    level: Level = Level.INFO,
    message: str = "hello",
    *,
    extra: dict[str, object] | None = None,
    exception: str | None = None,
    stack_info: str | None = None,
) -> LogRecord:
    return LogRecord(
        level=level,
        message=message,
        logger_name="app.worker",
        extra=extra or {},
        exception=exception,
        stack_info=stack_info,
    )


class TestRichHandler:
    def test_writes_pretty_line(self):
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=False, color_system=None)
        handler = RichHandler(console=console)

        handler.handle(_rec(extra={"job_id": "a1"}))

        out = buf.getvalue()
        assert "INFO" in out
        assert "app.worker" in out
        assert "hello" in out
        assert "job_id" in out

    def test_can_hide_extra_fields(self):
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=False, color_system=None)
        handler = RichHandler(console=console, show_extra=False)

        handler.handle(_rec(extra={"job_id": "a1"}))

        assert "job_id" not in buf.getvalue()

    def test_custom_formatter_is_respected(self):
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=False, color_system=None)
        handler = RichHandler(console=console)
        handler.set_formatter(JSONFormatter())

        handler.handle(_rec(level=Level.ERROR, extra={"job_id": "a1"}))

        out = buf.getvalue()
        assert '"message": "hello"' in out
        assert '"job_id": "a1"' in out

    def test_exception_and_stack_are_rendered(self):
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=False, color_system=None)
        handler = RichHandler(console=console)

        handler.handle(
            _rec(
                level=Level.ERROR,
                exception="ValueError: boom",
                stack_info="frame one",
            )
        )

        out = buf.getvalue()
        assert "ValueError: boom" in out
        assert "Stack (most recent call last):" in out
        assert "frame one" in out

    def test_package_export_is_available(self):
        assert RichHandler.__name__ == "RichHandler"
