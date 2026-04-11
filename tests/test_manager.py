import io
import json

from mollog import JSONFormatter, StreamHandler, clear_context, configure, get_logger, shutdown
from mollog.manager import LoggerManager


class TestConfigureAndShutdown:
    def setup_method(self) -> None:
        LoggerManager()._reset()
        clear_context()

    def test_configure_with_string_level_and_formatter(self):
        buf = io.StringIO()
        handler = StreamHandler(stream=buf)

        root = configure(level="debug", handlers=[handler], formatter=JSONFormatter())
        logger = get_logger("app")
        logger.info("configured", release="1.0.0")

        assert root is LoggerManager().root
        data = json.loads(buf.getvalue().strip())
        assert data["message"] == "configured"
        assert data["release"] == "1.0.0"

    def test_shutdown_closes_and_clears_handlers(self):
        class ClosingHandler(StreamHandler):
            def __init__(self, stream: io.StringIO) -> None:
                super().__init__(stream=stream)
                self.closed = False

            def close(self) -> None:
                self.closed = True

        buf = io.StringIO()
        handler = ClosingHandler(buf)
        configure(handlers=[handler])

        shutdown()

        assert handler.closed is True
        assert LoggerManager().root.handlers == []

    def test_configure_without_replace_does_not_duplicate_default_handler(self):
        configure(level="info")
        original = list(LoggerManager().root.handlers)

        configure(level="debug", replace=False)

        assert LoggerManager().root.handlers == original
