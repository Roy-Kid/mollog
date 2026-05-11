"""Top-level convenience API: log helpers, set_level, level constants,
stdlib %-style format strings, and the stdlib-logging bridge.

These tests prove the user can replace `import logging` calls entirely:

    mollog.configure(level="INFO", format="%(asctime)s %(levelname)s %(name)s %(message)s")
    mollog.get_logger("httpx").set_level("WARNING")
    mollog.info("hello")
"""

from __future__ import annotations

import io
import logging as stdlib_logging
import re

import pytest

import mollog
from mollog import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    TRACE,
    WARNING,
    Level,
    StdlibStyleFormatter,
)
from mollog._manager import LoggerManager
from mollog._stdlib_bridge import (
    StdlibBridgeHandler,
    capture_stdlib_logging,
    release_stdlib_logging,
)


def _clear_stdlib_state() -> None:
    """Wipe stdlib logger state polluted by tests that call setLevel."""

    for existing in tuple(stdlib_logging.getLogger().handlers):
        stdlib_logging.getLogger().removeHandler(existing)
    stdlib_logging.getLogger().setLevel(stdlib_logging.WARNING)
    for name, logger in list(stdlib_logging.Logger.manager.loggerDict.items()):
        if isinstance(logger, stdlib_logging.PlaceHolder):
            continue
        logger.setLevel(stdlib_logging.NOTSET)
        logger.disabled = False
        for h in tuple(logger.handlers):
            logger.removeHandler(h)


@pytest.fixture(autouse=True)
def _reset_state():
    _clear_stdlib_state()
    LoggerManager()._reset()
    yield
    LoggerManager()._reset()
    release_stdlib_logging()
    _clear_stdlib_state()


# ──────────────────────────────────────────────────────────────────────
# Level constants
# ──────────────────────────────────────────────────────────────────────


class TestLevelConstants:
    def test_constants_are_identical_to_stdlib_logging(self) -> None:
        # Plain `int` objects — same identity as stdlib's, not a
        # re-invented `Level` enum substitute.
        assert mollog.NOTSET is stdlib_logging.NOTSET
        assert mollog.DEBUG is stdlib_logging.DEBUG
        assert mollog.INFO is stdlib_logging.INFO
        assert mollog.WARNING is stdlib_logging.WARNING
        assert mollog.WARN is stdlib_logging.WARN
        assert mollog.ERROR is stdlib_logging.ERROR
        assert mollog.CRITICAL is stdlib_logging.CRITICAL
        assert mollog.FATAL is stdlib_logging.FATAL
        for const in (
            mollog.NOTSET,
            mollog.DEBUG,
            mollog.INFO,
            mollog.WARNING,
            mollog.WARN,
            mollog.ERROR,
            mollog.CRITICAL,
            mollog.FATAL,
        ):
            assert type(const) is int

    def test_trace_is_mollog_superset_addition(self) -> None:
        # stdlib has no TRACE — this is mollog's superset addition. It
        # must still be a plain int, and Level.coerce must accept it.
        assert TRACE == 5
        assert type(TRACE) is int
        assert Level.coerce(TRACE) is Level.TRACE

    def test_constants_coerce_back_to_level_for_internal_use(self) -> None:
        # Plain-int constants must still feed `Level.coerce` cleanly so
        # internal mollog code keeps its enum-typed representation.
        assert Level.coerce(DEBUG) is Level.DEBUG
        assert Level.coerce(INFO) is Level.INFO
        assert Level.coerce(WARNING) is Level.WARNING
        assert Level.coerce(ERROR) is Level.ERROR
        assert Level.coerce(CRITICAL) is Level.CRITICAL

    def test_constants_in_dunder_all(self) -> None:
        for name in (
            "NOTSET",
            "TRACE",
            "DEBUG",
            "INFO",
            "WARNING",
            "WARN",
            "ERROR",
            "CRITICAL",
            "FATAL",
        ):
            assert name in mollog.__all__


# ──────────────────────────────────────────────────────────────────────
# Top-level log functions
# ──────────────────────────────────────────────────────────────────────


class TestTopLevelLogFunctions:
    def test_module_level_info_writes_through_root(self) -> None:
        buf = io.StringIO()
        mollog.configure(level="DEBUG", stream=buf, capture_stdlib=False)
        mollog.info("from-module", flow="checkout")
        assert "from-module" in buf.getvalue()
        assert "flow=checkout" in buf.getvalue()

    def test_module_level_warning_respects_root_level(self) -> None:
        buf = io.StringIO()
        mollog.configure(level="WARNING", stream=buf, capture_stdlib=False)
        mollog.info("dropped")
        mollog.warning("kept")
        assert "dropped" not in buf.getvalue()
        assert "kept" in buf.getvalue()

    def test_module_level_set_level_changes_root(self) -> None:
        mollog.configure(level="WARNING", stream=io.StringIO(), capture_stdlib=False)
        assert LoggerManager().root.level is Level.WARNING
        mollog.set_level("DEBUG")
        assert LoggerManager().root.level is Level.DEBUG

    def test_exception_renders_traceback(self) -> None:
        buf = io.StringIO()
        mollog.configure(level="DEBUG", stream=buf, capture_stdlib=False)
        try:
            raise RuntimeError("boom")
        except RuntimeError:
            mollog.exception("caught")
        out = buf.getvalue()
        assert "caught" in out
        assert "RuntimeError: boom" in out


# ──────────────────────────────────────────────────────────────────────
# Logger.set_level
# ──────────────────────────────────────────────────────────────────────


class TestLoggerSetLevel:
    def test_set_level_accepts_string(self) -> None:
        log = mollog.get_logger("svc")
        log.set_level("WARNING")
        assert log.level is Level.WARNING

    def test_set_level_accepts_int(self) -> None:
        log = mollog.get_logger("svc")
        log.set_level(stdlib_logging.ERROR)
        assert log.level is Level.ERROR

    def test_set_level_propagates_to_stdlib_logger(self) -> None:
        # Even before installing the bridge, we propagate so stdlib drops
        # noisy library logs at the source.
        log = mollog.get_logger("httpx")
        log.set_level("WARNING")
        assert stdlib_logging.getLogger("httpx").level == stdlib_logging.WARNING

    def test_bind_view_set_level_mirrors_underlying_logger(self) -> None:
        # On the new design Logger.bind() returns a Logger view sharing
        # state. Setting the level on the view propagates to its name.
        log = mollog.get_logger("svc")
        view = log.bind(component="ingest")
        view.set_level("CRITICAL")
        assert view.level is Level.CRITICAL


# ──────────────────────────────────────────────────────────────────────
# configure(format=...) — stdlib %-style strings
# ──────────────────────────────────────────────────────────────────────


class TestStdlibFormat:
    def test_configure_accepts_stdlib_format_string(self) -> None:
        buf = io.StringIO()
        mollog.configure(
            level="INFO",
            stream=buf,
            format="%(levelname)s %(name)s %(message)s",
            capture_stdlib=False,
        )
        mollog.get_logger("svc").info("hello")
        line = buf.getvalue().strip()
        assert line == "INFO svc hello"

    def test_configure_format_respects_asctime(self) -> None:
        buf = io.StringIO()
        mollog.configure(
            level="INFO",
            stream=buf,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d",
            capture_stdlib=False,
        )
        mollog.get_logger("svc").info("hi")
        line = buf.getvalue().strip()
        assert re.match(r"\d{4}-\d{2}-\d{2} \| INFO \| svc \| hi$", line), line

    def test_format_and_formatter_are_mutually_exclusive(self) -> None:
        from mollog import JSONFormatter

        with pytest.raises(ValueError):
            mollog.configure(
                level="INFO",
                stream=io.StringIO(),
                format="%(message)s",
                formatter=JSONFormatter(),
                capture_stdlib=False,
            )

    def test_stdlib_style_formatter_can_be_used_directly(self) -> None:
        buf = io.StringIO()
        formatter = StdlibStyleFormatter("%(levelname)s::%(message)s")
        mollog.configure(
            level="INFO",
            stream=buf,
            formatter=formatter,
            capture_stdlib=False,
        )
        mollog.get_logger("svc").info("x")
        assert buf.getvalue().strip() == "INFO::x"


# ──────────────────────────────────────────────────────────────────────
# Stdlib bridge: capture stdlib `logging` records into mollog
# ──────────────────────────────────────────────────────────────────────


class TestStdlibBridge:
    def test_configure_installs_bridge_by_default(self) -> None:
        mollog.configure(level="INFO", stream=io.StringIO())
        root = stdlib_logging.getLogger()
        assert any(isinstance(h, StdlibBridgeHandler) for h in root.handlers)

    def test_capture_stdlib_false_skips_bridge(self) -> None:
        mollog.configure(level="INFO", stream=io.StringIO(), capture_stdlib=False)
        root = stdlib_logging.getLogger()
        assert not any(isinstance(h, StdlibBridgeHandler) for h in root.handlers)

    def test_stdlib_records_flow_through_mollog(self) -> None:
        buf = io.StringIO()
        mollog.configure(level="DEBUG", stream=buf)
        stdlib_logging.getLogger("httpx").info("third-party-line")
        assert "third-party-line" in buf.getvalue()
        assert "httpx" in buf.getvalue()

    def test_set_level_on_named_mollog_logger_silences_stdlib_source(self) -> None:
        buf = io.StringIO()
        mollog.configure(level="DEBUG", stream=buf)
        mollog.get_logger("httpx").set_level("WARNING")

        stdlib_logging.getLogger("httpx").info("noisy")
        stdlib_logging.getLogger("httpx").warning("important")

        out = buf.getvalue()
        assert "noisy" not in out
        assert "important" in out

    def test_release_stdlib_logging_is_idempotent(self) -> None:
        capture_stdlib_logging()
        release_stdlib_logging()
        release_stdlib_logging()  # no-op
        root = stdlib_logging.getLogger()
        assert not any(isinstance(h, StdlibBridgeHandler) for h in root.handlers)

    def test_bridge_preserves_exc_info(self) -> None:
        buf = io.StringIO()
        mollog.configure(level="DEBUG", stream=buf)
        try:
            raise ValueError("bridged")
        except ValueError:
            stdlib_logging.getLogger("svc").exception("oops")
        out = buf.getvalue()
        assert "oops" in out
        assert "ValueError: bridged" in out

    def test_shutdown_removes_bridge(self) -> None:
        mollog.configure(level="INFO", stream=io.StringIO())
        mollog.shutdown()
        root = stdlib_logging.getLogger()
        assert not any(isinstance(h, StdlibBridgeHandler) for h in root.handlers)


# ──────────────────────────────────────────────────────────────────────
# End-to-end: the user's migration scenario
# ──────────────────────────────────────────────────────────────────────


# ──────────────────────────────────────────────────────────────────────
# Stdlib drop-in surface: getLogger, basicConfig, camelCase Logger API
# ──────────────────────────────────────────────────────────────────────


class TestStdlibDropInSurface:
    def test_getLogger_returns_root_for_none(self) -> None:
        root = mollog.getLogger()
        assert root is LoggerManager().root
        assert mollog.getLogger(None) is root

    def test_getLogger_returns_named_logger(self) -> None:
        log = mollog.getLogger("svc.api")
        assert log.name == "svc.api"
        assert log is mollog.get_logger("svc.api")

    def test_basicConfig_returns_none(self) -> None:
        result = mollog.basicConfig(level=mollog.INFO, stream=io.StringIO())
        assert result is None

    def test_basicConfig_is_noop_when_handlers_present(self) -> None:
        first_buf = io.StringIO()
        mollog.basicConfig(level="INFO", stream=first_buf)
        # second call without force is a no-op — original stream stays attached
        second_buf = io.StringIO()
        mollog.basicConfig(level="INFO", stream=second_buf)
        mollog.get_logger("svc").info("hello")
        assert "hello" in first_buf.getvalue()
        assert second_buf.getvalue() == ""

    def test_basicConfig_force_replaces_handlers(self) -> None:
        first_buf = io.StringIO()
        mollog.basicConfig(level="INFO", stream=first_buf)
        second_buf = io.StringIO()
        mollog.basicConfig(level="INFO", stream=second_buf, force=True)
        mollog.get_logger("svc").info("hello")
        assert "hello" not in first_buf.getvalue()
        assert "hello" in second_buf.getvalue()

    def test_basicConfig_accepts_stdlib_format(self) -> None:
        buf = io.StringIO()
        mollog.basicConfig(
            level="INFO",
            stream=buf,
            format="%(levelname)s %(name)s %(message)s",
        )
        mollog.get_logger("svc").info("hi")
        assert buf.getvalue().strip() == "INFO svc hi"

    def test_basicConfig_rejects_stream_and_filename_together(self) -> None:
        with pytest.raises(ValueError, match="mutually exclusive"):
            mollog.basicConfig(stream=io.StringIO(), filename="/tmp/x.log")

    def test_basicConfig_rejects_unknown_kwargs(self) -> None:
        with pytest.raises(ValueError, match="Unrecognised"):
            mollog.basicConfig(level="INFO", banana="yes")  # type: ignore[arg-type]

    def test_basicConfig_rejects_non_percent_style(self) -> None:
        with pytest.raises(ValueError, match="style"):
            mollog.basicConfig(level="INFO", style="{")

    def test_import_mollog_as_logging_pattern(self) -> None:
        """The full drop-in: `import mollog as logging` should just work."""

        logging = mollog  # noqa: N806 — simulates `import mollog as logging`
        buf = io.StringIO()
        logging.basicConfig(level=logging.INFO, stream=buf, format="%(message)s")
        log = logging.getLogger(__name__)
        log.setLevel(logging.WARNING)
        log.info("dropped")
        log.warning("kept")
        out = buf.getvalue()
        assert "dropped" not in out
        assert "kept" in out

    def test_logger_camelcase_aliases_share_state_with_snake_case(self) -> None:
        log = mollog.get_logger("svc")
        log.setLevel("WARNING")
        assert log.level is Level.WARNING
        assert log.isEnabledFor(Level.ERROR)
        assert not log.isEnabledFor(Level.INFO)

        from mollog._handler import StreamHandler

        handler = StreamHandler(stream=io.StringIO())
        log.addHandler(handler)
        assert handler in log.handlers
        log.removeHandler(handler)
        assert handler not in log.handlers

    def test_logger_getChild_builds_dotted_name(self) -> None:
        parent = mollog.getLogger("svc")
        child = parent.getChild("api")
        assert child.name == "svc.api"
        assert child.parent is parent

    def test_logger_getChild_from_root_drops_leading_dot(self) -> None:
        root = mollog.getLogger()
        child = root.getChild("svc")
        assert child.name == "svc"

    def test_logger_hasHandlers_walks_ancestors(self) -> None:
        mollog.basicConfig(level="INFO", stream=io.StringIO())
        child = mollog.getLogger("svc.api")
        assert child.handlers == []
        assert child.hasHandlers()  # inherits from root


def test_user_migration_scenario_works_without_importing_logging() -> None:
    """The exact replacement requested by the user — no `import logging`.

    Old:
        mollog.configure(level="INFO")
        logging.basicConfig(level=logging.WARNING, format="...")
        logging.getLogger("httpx").setLevel(logging.WARNING)

    New:
        mollog.configure(level="INFO", format="...")
        mollog.get_logger("httpx").set_level("WARNING")
    """

    buf = io.StringIO()
    mollog.configure(
        level="INFO",
        stream=buf,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    mollog.get_logger("httpx").set_level("WARNING")

    # App code: visible at INFO.
    mollog.get_logger("app").info("startup")
    # Library code emits via stdlib logging — silenced by the per-logger level.
    stdlib_logging.getLogger("httpx").info("HTTP/1.1 200 OK")
    stdlib_logging.getLogger("httpx").warning("rate-limited")

    out = buf.getvalue()
    assert "startup" in out
    assert "HTTP/1.1 200 OK" not in out
    assert "rate-limited" in out
