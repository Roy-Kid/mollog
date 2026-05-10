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
from mollog.manager import LoggerManager
from mollog.stdlib_bridge import (
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
    def test_constants_are_level_enum_members(self) -> None:
        assert TRACE is Level.TRACE
        assert DEBUG is Level.DEBUG
        assert INFO is Level.INFO
        assert WARNING is Level.WARNING
        assert ERROR is Level.ERROR
        assert CRITICAL is Level.CRITICAL

    def test_constants_in_dunder_all(self) -> None:
        for name in ("TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
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

    def test_bound_logger_set_level_proxies_to_underlying(self) -> None:
        log = mollog.get_logger("svc")
        bound = log.bind(component="ingest")
        bound.set_level("CRITICAL")
        assert log.level is Level.CRITICAL


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
        # asctime renders the formatted timestamp; we only assert shape.
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
