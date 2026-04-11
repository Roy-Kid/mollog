import io
import json

from mollog.handler import StreamHandler
from mollog.level import Level
from mollog.logger import BoundLogger, Logger
from mollog.manager import LoggerManager


class TestLogger:
    def test_basic_logging(self):
        buf = io.StringIO()
        logger = Logger("app")
        logger.add_handler(StreamHandler(stream=buf))
        logger.info("hello")
        assert "hello" in buf.getvalue()

    def test_level_filtering(self):
        buf = io.StringIO()
        logger = Logger("app", level=Level.WARNING)
        logger.add_handler(StreamHandler(stream=buf))
        logger.debug("nope")
        assert buf.getvalue() == ""
        logger.warning("yes")
        assert "yes" in buf.getvalue()

    def test_propagation(self):
        parent_buf = io.StringIO()
        child_buf = io.StringIO()
        parent = Logger("a")
        parent.add_handler(StreamHandler(stream=parent_buf))
        child = Logger("a.b")
        child.add_handler(StreamHandler(stream=child_buf))
        child.parent = parent
        child.info("msg")
        assert "msg" in child_buf.getvalue()
        assert "msg" in parent_buf.getvalue()

    def test_propagation_disabled(self):
        parent_buf = io.StringIO()
        parent = Logger("a")
        parent.add_handler(StreamHandler(stream=parent_buf))
        child = Logger("a.b", propagate=False)
        child.parent = parent
        child_buf = io.StringIO()
        child.add_handler(StreamHandler(stream=child_buf))
        child.info("msg")
        assert "msg" in child_buf.getvalue()
        assert parent_buf.getvalue() == ""

    def test_all_level_methods(self):
        buf = io.StringIO()
        logger = Logger("t")
        logger.add_handler(StreamHandler(stream=buf))
        logger.trace("1")
        logger.debug("2")
        logger.info("3")
        logger.warning("4")
        logger.error("5")
        logger.critical("6")
        out = buf.getvalue()
        for n in ["1", "2", "3", "4", "5", "6"]:
            assert n in out

    def test_remove_handler(self):
        buf = io.StringIO()
        handler = StreamHandler(stream=buf)
        logger = Logger("app")
        logger.add_handler(handler)
        logger.remove_handler(handler)
        logger.info("hidden")
        assert buf.getvalue() == ""

    def test_exception_shortcut(self):
        buf = io.StringIO()
        from mollog.formatter import JSONFormatter

        logger = Logger("app")
        handler = StreamHandler(stream=buf)
        handler.set_formatter(JSONFormatter())
        logger.add_handler(handler)

        try:
            raise ValueError("boom")
        except ValueError:
            logger.exception("failed", job_id="a1")

        data = json.loads(buf.getvalue().strip())
        assert data["message"] == "failed"
        assert data["job_id"] == "a1"
        assert "ValueError: boom" in data["exception"]

    def test_exc_info_and_stack_info(self):
        buf = io.StringIO()
        from mollog.formatter import JSONFormatter

        logger = Logger("app")
        handler = StreamHandler(stream=buf)
        handler.set_formatter(JSONFormatter())
        logger.add_handler(handler)

        try:
            raise RuntimeError("bad")
        except RuntimeError:
            logger.error("captured", exc_info=True, stack_info=True)

        data = json.loads(buf.getvalue().strip())
        assert "RuntimeError: bad" in data["exception"]
        assert "test_exc_info_and_stack_info" in data["stack_info"]


class TestBoundLogger:
    def test_bind_adds_extra(self):
        buf = io.StringIO()
        from mollog.formatter import JSONFormatter

        logger = Logger("app")
        h = StreamHandler(stream=buf)
        h.set_formatter(JSONFormatter())
        logger.add_handler(h)
        bound = logger.bind(request_id="abc")
        assert isinstance(bound, BoundLogger)
        bound.info("started")
        assert '"request_id": "abc"' in buf.getvalue()

    def test_nested_bind(self):
        buf = io.StringIO()
        from mollog.formatter import JSONFormatter

        logger = Logger("app")
        h = StreamHandler(stream=buf)
        h.set_formatter(JSONFormatter())
        logger.add_handler(h)
        b1 = logger.bind(a="1")
        b2 = b1.bind(b="2")
        b2.info("x")
        out = buf.getvalue()
        assert '"a": "1"' in out
        assert '"b": "2"' in out

    def test_bound_logger_exception(self):
        buf = io.StringIO()
        from mollog.formatter import JSONFormatter

        logger = Logger("app")
        handler = StreamHandler(stream=buf)
        handler.set_formatter(JSONFormatter())
        logger.add_handler(handler)
        bound = logger.bind(request_id="abc")

        try:
            raise KeyError("missing")
        except KeyError:
            bound.exception("lookup failed")

        data = json.loads(buf.getvalue().strip())
        assert data["request_id"] == "abc"
        assert "KeyError" in data["exception"]


class TestLoggerManager:
    def setup_method(self):
        LoggerManager()._reset()

    def test_same_logger_returned(self):
        mgr = LoggerManager()
        a = mgr.get_logger("app")
        b = mgr.get_logger("app")
        assert a is b

    def test_hierarchy(self):
        mgr = LoggerManager()
        child = mgr.get_logger("a.b.c")
        assert child.parent is not None
        assert child.parent.name == "a.b"
        assert child.parent.parent is not None
        assert child.parent.parent.name == "a"
        assert child.parent.parent.parent is mgr.root

    def test_root_logger(self):
        mgr = LoggerManager()
        root = mgr.get_logger("")
        assert root is mgr.root
