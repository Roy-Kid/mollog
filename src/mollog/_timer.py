"""Lightweight wall-clock timer for instrumenting code blocks."""

from __future__ import annotations

import time
from types import TracebackType
from typing import Self

from mollog._level import Level
from mollog._manager import get_logger

_LEVEL_METHODS: dict[Level, str] = {
    Level.TRACE: "trace",
    Level.DEBUG: "debug",
    Level.INFO: "info",
    Level.WARNING: "warning",
    Level.ERROR: "error",
    Level.CRITICAL: "critical",
}


class Timer:
    """Measure elapsed wall-clock time with a context manager or explicitly.

    The timer reads :func:`time.perf_counter` on start and stop. By default
    it logs ``"<name> took <seconds>s"`` at INFO when stopped; pass
    ``log=False`` to use it as a silent stopwatch and read
    :attr:`elapsed` yourself.

    Examples:
        Context-manager (logs on exit)::

            with Timer("fetch"):
                do_work()

        Explicit start/stop, silent::

            t = Timer("fetch", log=False).start()
            do_work()
            t.stop()
            elapsed_seconds = t.elapsed
    """

    def __init__(
        self,
        name: str,
        *,
        log: bool = True,
        level: Level = Level.INFO,
        logger_name: str = "mollog.timer",
    ) -> None:
        self.name = name
        self.log = log
        self.level = level
        self._logger = get_logger(logger_name)
        self._start: float | None = None
        self._end: float | None = None

    def start(self) -> Self:
        """Start (or restart) the timer. Returns ``self`` for chaining."""
        self._start = time.perf_counter()
        self._end = None
        return self

    def stop(self) -> float:
        """Stop the timer, optionally log, return elapsed seconds."""
        if self._start is None:
            raise RuntimeError(f"Timer {self.name!r} has not been started")
        self._end = time.perf_counter()
        elapsed = self._end - self._start
        if self.log:
            message = f"{self.name} took {elapsed:.3f}s"
            method = _LEVEL_METHODS[self.level]
            getattr(self._logger, method)(message)
        return elapsed

    @property
    def elapsed(self) -> float:
        """Elapsed seconds. Returns 0.0 before :meth:`start`, live while running."""
        if self._start is None:
            return 0.0
        end = self._end if self._end is not None else time.perf_counter()
        return end - self._start

    @property
    def running(self) -> bool:
        """True between :meth:`start` and :meth:`stop`."""
        return self._start is not None and self._end is None

    def __enter__(self) -> Self:
        return self.start()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.stop()
