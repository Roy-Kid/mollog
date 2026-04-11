import io

from mollog.filter import LevelFilter
from mollog.handler import NullHandler, StreamHandler
from mollog.level import Level
from mollog.record import LogRecord


def _rec(level: Level = Level.INFO) -> LogRecord:
    return LogRecord(level=level, message="hi", logger_name="t")


class TestStreamHandler:
    def test_writes_to_stream(self):
        buf = io.StringIO()
        h = StreamHandler(stream=buf)
        h.handle(_rec())
        assert "hi" in buf.getvalue()
        assert buf.getvalue().endswith("\n")

    def test_level_gate(self):
        buf = io.StringIO()
        h = StreamHandler(stream=buf, level=Level.WARNING)
        h.handle(_rec(Level.DEBUG))
        assert buf.getvalue() == ""

    def test_filter_blocks(self):
        buf = io.StringIO()
        h = StreamHandler(stream=buf)
        h.add_filter(LevelFilter(min_level=Level.ERROR))
        h.handle(_rec(Level.INFO))
        assert buf.getvalue() == ""

    def test_remove_and_clear_filters(self):
        buf = io.StringIO()
        filt = LevelFilter(min_level=Level.ERROR)
        h = StreamHandler(stream=buf)
        h.add_filter(filt)
        h.remove_filter(filt)
        h.handle(_rec(Level.INFO))
        assert "hi" in buf.getvalue()

        h.clear_filters()
        h.handle(_rec(Level.INFO))
        assert buf.getvalue().count("hi") == 2


class TestNullHandler:
    def test_no_error(self):
        h = NullHandler()
        h.handle(_rec())  # should not raise

    def test_context_manager_closes(self):
        class ClosingHandler(NullHandler):
            def __init__(self) -> None:
                super().__init__()
                self.closed = False

            def close(self) -> None:
                self.closed = True

        handler = ClosingHandler()
        with handler:
            handler.handle(_rec())
        assert handler.closed is True
