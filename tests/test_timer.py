"""Tests for ``mollog.Timer``."""

from __future__ import annotations

import io
import time

import pytest

from mollog import StreamHandler, Timer, get_logger


def test_context_manager_records_elapsed() -> None:
    with Timer("t", log=False) as t:
        time.sleep(0.01)
    assert t.elapsed >= 0.01
    assert not t.running


def test_explicit_start_stop_returns_elapsed() -> None:
    t = Timer("t", log=False).start()
    time.sleep(0.01)
    elapsed = t.stop()
    assert elapsed >= 0.01
    assert t.elapsed == pytest.approx(elapsed, abs=1e-6)


def test_elapsed_is_live_while_running() -> None:
    t = Timer("t", log=False).start()
    time.sleep(0.01)
    live = t.elapsed
    assert live >= 0.01
    assert t.running
    t.stop()


def test_elapsed_zero_before_start() -> None:
    t = Timer("t", log=False)
    assert t.elapsed == 0.0
    assert not t.running


def test_stop_without_start_raises() -> None:
    t = Timer("t", log=False)
    with pytest.raises(RuntimeError, match="has not been started"):
        t.stop()


def test_restart_clears_previous_end() -> None:
    t = Timer("t", log=False).start()
    t.stop()
    first = t.elapsed
    t.start()
    assert t.running
    time.sleep(0.005)
    second = t.stop()
    assert second != first


def test_logs_on_exit_by_default() -> None:
    buf = io.StringIO()
    logger = get_logger("mollog.timer")
    handler = StreamHandler(stream=buf)
    logger.add_handler(handler)
    try:
        with Timer("fetch"):
            pass
    finally:
        logger.remove_handler(handler)
    assert "fetch took" in buf.getvalue()


def test_silent_when_log_false() -> None:
    buf = io.StringIO()
    logger = get_logger("mollog.timer")
    handler = StreamHandler(stream=buf)
    logger.add_handler(handler)
    try:
        with Timer("fetch", log=False):
            pass
    finally:
        logger.remove_handler(handler)
    assert buf.getvalue() == ""
