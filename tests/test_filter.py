from mollog.filter import Filter, LevelFilter
from mollog.level import Level
from mollog.record import LogRecord


def _rec(level: Level = Level.INFO) -> LogRecord:
    return LogRecord(level=level, message="m", logger_name="t")


class TestLevelFilter:
    def test_min_level(self):
        f = LevelFilter(min_level=Level.WARNING)
        assert f.filter(_rec(Level.WARNING)) is True
        assert f.filter(_rec(Level.ERROR)) is True
        assert f.filter(_rec(Level.DEBUG)) is False

    def test_max_level(self):
        f = LevelFilter(max_level=Level.WARNING)
        assert f.filter(_rec(Level.INFO)) is True
        assert f.filter(_rec(Level.WARNING)) is True
        assert f.filter(_rec(Level.ERROR)) is False

    def test_range(self):
        f = LevelFilter(min_level=Level.INFO, max_level=Level.WARNING)
        assert f.filter(_rec(Level.DEBUG)) is False
        assert f.filter(_rec(Level.INFO)) is True
        assert f.filter(_rec(Level.WARNING)) is True
        assert f.filter(_rec(Level.ERROR)) is False

    def test_no_bounds(self):
        f = LevelFilter()
        assert f.filter(_rec(Level.TRACE)) is True


class TestCustomFilter:
    def test_subclass(self):
        class NoSecret(Filter):
            def filter(self, record: LogRecord) -> bool:
                return not record.extra.get("secret")

        f = NoSecret()
        assert f.filter(_rec()) is True
        r = LogRecord(level=Level.INFO, message="x", logger_name="t", extra={"secret": True})
        assert f.filter(r) is False
