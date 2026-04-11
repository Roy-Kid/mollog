import io
import json

from mollog.context import scoped_context
from mollog.filter import LevelFilter
from mollog.formatter import JSONFormatter, TextFormatter
from mollog.handler import StreamHandler
from mollog.level import Level
from mollog.logger import Logger
from mollog.manager import LoggerManager, get_logger


class TestIntegration:
    def setup_method(self):
        LoggerManager()._reset()

    def test_multiple_handlers(self):
        text_buf = io.StringIO()
        json_buf = io.StringIO()

        logger = Logger("app", level=Level.DEBUG)

        th = StreamHandler(stream=text_buf)
        th.set_formatter(TextFormatter())
        logger.add_handler(th)

        jh = StreamHandler(stream=json_buf)
        jh.set_formatter(JSONFormatter())
        logger.add_handler(jh)

        logger.info("dual")

        assert "dual" in text_buf.getvalue()
        data = json.loads(json_buf.getvalue().strip())
        assert data["message"] == "dual"

    def test_hierarchy_with_handlers(self):
        root_buf = io.StringIO()
        child_buf = io.StringIO()

        mgr = LoggerManager()
        root = mgr.get_logger("")
        root.add_handler(StreamHandler(stream=root_buf))

        child = mgr.get_logger("app.db")
        child.add_handler(StreamHandler(stream=child_buf))

        child.info("query")

        assert "query" in child_buf.getvalue()
        assert "query" in root_buf.getvalue()

    def test_bind_context(self):
        buf = io.StringIO()
        logger = Logger("app")
        h = StreamHandler(stream=buf)
        h.set_formatter(JSONFormatter())
        logger.add_handler(h)

        bound = logger.bind(step=42, molecule_id="H2O")
        bound.info("energy computed")

        data = json.loads(buf.getvalue().strip())
        assert data["step"] == 42
        assert data["molecule_id"] == "H2O"
        assert data["message"] == "energy computed"

    def test_get_logger_quick_start(self, capsys):
        logger = get_logger("myapp")
        logger.info("quickstart")
        # default handler writes to stderr
        captured = capsys.readouterr()
        assert "quickstart" in captured.err

    def test_filter_with_handler(self):
        err_buf = io.StringIO()
        all_buf = io.StringIO()

        logger = Logger("app")

        err_handler = StreamHandler(stream=err_buf)
        err_handler.add_filter(LevelFilter(min_level=Level.ERROR))
        logger.add_handler(err_handler)

        all_handler = StreamHandler(stream=all_buf)
        logger.add_handler(all_handler)

        logger.info("normal")
        logger.error("bad")

        assert "normal" not in err_buf.getvalue()
        assert "bad" in err_buf.getvalue()
        assert "normal" in all_buf.getvalue()
        assert "bad" in all_buf.getvalue()

    def test_scoped_context_with_bound_logger(self):
        buf = io.StringIO()
        logger = Logger("app")
        handler = StreamHandler(stream=buf)
        handler.set_formatter(JSONFormatter())
        logger.add_handler(handler)

        with scoped_context(request_id="req-1"):
            logger.bind(component="worker").info("running")

        data = json.loads(buf.getvalue().strip())
        assert data["request_id"] == "req-1"
        assert data["component"] == "worker"
