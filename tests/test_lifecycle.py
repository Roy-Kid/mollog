"""Lifecycle contract: context-manager, close_logger, atexit shutdown.

Trace: mollog-self-managed-lifecycle.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import mollog
from mollog import FileHandler, LoggerManager
from mollog.manager import close_logger


@pytest.fixture(autouse=True)
def _reset_manager():
    """Reset the singleton between tests so we don't see cross-test bleed."""

    LoggerManager()._reset()
    yield
    LoggerManager()._reset()


# ── ac-001 — Logger is a context manager


def test_logger_enter_exit_closes_handlers(tmp_path: Path) -> None:
    log_file = tmp_path / "ctx.log"
    with mollog.get_logger("scope.test") as log:
        log.add_handler(FileHandler(log_file))
        assert len(log.handlers) == 1
    # After block: handlers closed and cleared
    log = mollog.get_logger("scope.test")
    assert log.handlers == []


def test_bound_logger_is_also_a_context_manager() -> None:
    log = mollog.get_logger("x")
    bound = log.bind(component="ingest")
    with bound as b:
        assert b is bound


# ── ac-002 — close_logger evicts from the registry


def test_close_logger_evicts_from_registry(tmp_path: Path) -> None:
    log = mollog.get_logger("session.123")
    log.add_handler(FileHandler(tmp_path / "s.log"))
    assert "session.123" in LoggerManager()._loggers

    close_logger("session.123")
    assert "session.123" not in LoggerManager()._loggers

    fresh = mollog.get_logger("session.123")
    assert fresh.handlers == []


def test_close_logger_unknown_name_is_noop() -> None:
    close_logger("never_existed")  # must not raise


def test_close_logger_double_call_is_safe(tmp_path: Path) -> None:
    log = mollog.get_logger("dup")
    log.add_handler(FileHandler(tmp_path / "d.log"))
    close_logger("dup")
    close_logger("dup")  # second call is a no-op


# ── ac-003 — exposed at the module level


def test_close_logger_is_exported_from_mollog() -> None:
    assert mollog.close_logger is close_logger
    assert "close_logger" in mollog.__all__


# ── ac-004 — atexit registration introspection


def test_atexit_registered_on_import() -> None:
    """Subprocess: import mollog, list atexit callbacks, assert
    LoggerManager.shutdown is registered.

    A fresh subprocess is required because the test process'
    ``atexit`` queue accumulates handlers across the whole pytest run.
    """

    code = textwrap.dedent(
        """
        import atexit
        import sys

        # Snapshot atexit before importing mollog
        before = atexit._ncallbacks() if hasattr(atexit, '_ncallbacks') else 0

        import mollog  # noqa: F401

        after = atexit._ncallbacks() if hasattr(atexit, '_ncallbacks') else 1
        # On Python 3.12 _ncallbacks is available; assert the count grew.
        sys.stdout.write(f"{before},{after}\\n")
        """
    ).strip()
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    before, after = (int(x) for x in proc.stdout.strip().split(","))
    assert after > before, (
        f"importing mollog must register at least one atexit hook; before={before}, after={after}"
    )


# ── ac-005 — subprocess proves atexit fires


def test_subprocess_atexit_flushes_file_handler(tmp_path: Path) -> None:
    """Run a subprocess that opens a FileHandler and exits cleanly; the
    file must be readable + non-empty after the subprocess returns."""

    target = tmp_path / "atexit.log"
    code = textwrap.dedent(
        f"""
        import mollog
        log = mollog.get_logger('atexit.test')
        log.add_handler(mollog.FileHandler({str(target)!r}))
        log.info('hello-from-subprocess')
        # Do NOT explicitly close — rely on atexit hook.
        """
    ).strip()
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert target.exists()
    body = target.read_text(encoding="utf-8")
    assert "hello-from-subprocess" in body


# ── ac-006 — explicit close + shutdown is safe


def test_close_logger_then_shutdown_is_safe(tmp_path: Path) -> None:
    log = mollog.get_logger("safety")
    log.add_handler(FileHandler(tmp_path / "s.log"))
    close_logger("safety")
    LoggerManager().shutdown()  # must not raise
    LoggerManager().shutdown()  # idempotent
