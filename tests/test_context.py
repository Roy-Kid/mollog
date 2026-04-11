import io
import json

from mollog import (
    JSONFormatter,
    Logger,
    StreamHandler,
    bind_context,
    clear_context,
    get_context,
    reset_context,
    scoped_context,
)


class TestContext:
    def teardown_method(self) -> None:
        clear_context()

    def test_bind_context_injects_fields(self):
        buf = io.StringIO()
        logger = Logger("app")
        handler = StreamHandler(stream=buf)
        handler.set_formatter(JSONFormatter())
        logger.add_handler(handler)

        token = bind_context(request_id="req-1", trace_id="tr-1")
        try:
            logger.info("started")
        finally:
            reset_context(token)

        data = json.loads(buf.getvalue().strip())
        assert data["request_id"] == "req-1"
        assert data["trace_id"] == "tr-1"

    def test_scoped_context_restores_previous_state(self):
        token = bind_context(request_id="outer")
        try:
            with scoped_context(request_id="inner", user_id="u-1"):
                assert get_context()["request_id"] == "inner"
                assert get_context()["user_id"] == "u-1"
            assert get_context()["request_id"] == "outer"
            assert "user_id" not in get_context()
        finally:
            reset_context(token)

    def test_per_call_extra_overrides_context(self):
        buf = io.StringIO()
        logger = Logger("app")
        handler = StreamHandler(stream=buf)
        handler.set_formatter(JSONFormatter())
        logger.add_handler(handler)

        token = bind_context(request_id="outer")
        try:
            logger.info("started", request_id="inner")
        finally:
            reset_context(token)

        data = json.loads(buf.getvalue().strip())
        assert data["request_id"] == "inner"
