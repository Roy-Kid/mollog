from __future__ import annotations

import multiprocessing
import queue
import threading
from typing import Any

from mollog.handler import Handler
from mollog.level import Level
from mollog.record import LogRecord


class QueueHandler(Handler):
    """Handler that puts log records into a queue.

    Use with :class:`QueueListener` for thread/process-safe logging.
    """

    def __init__(
        self,
        q: queue.Queue[Any] | multiprocessing.Queue[Any],  # type: ignore[type-arg]
        level: Level = Level.TRACE,
    ) -> None:
        super().__init__(level)
        self._queue = q

    def emit(self, record: LogRecord) -> None:
        self._queue.put(record)


class QueueListener:
    """Consume records from a queue and dispatch to handlers.

    Runs a background thread.  Supports context-manager usage.
    """

    _SENTINEL = ("mollog", "stop")

    def __init__(
        self,
        q: queue.Queue[Any] | multiprocessing.Queue[Any],  # type: ignore[type-arg]
        *handlers: Handler,
        stop_grace_period: float = 0.1,
    ) -> None:
        if stop_grace_period < 0:
            raise ValueError("stop_grace_period must be greater than or equal to 0")
        self._queue = q
        self._handlers = list(handlers)
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._running = False
        self._stopping = False
        self._stop_grace_period = stop_grace_period

    def start(self) -> None:
        with self._lock:
            if self._running:
                raise RuntimeError("QueueListener is already running")
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._running = True
            self._stopping = False
            self._thread.start()

    def _run(self) -> None:
        draining = False
        try:
            while True:
                try:
                    if draining:
                        record = self._queue.get(timeout=self._stop_grace_period)
                    else:
                        record = self._queue.get()
                except queue.Empty:
                    if draining:
                        break
                    continue

                if record == self._SENTINEL:
                    draining = True
                    continue

                for h in self._handlers:
                    h.handle(record)
        finally:
            with self._lock:
                self._running = False
                self._stopping = False

    def stop(self) -> None:
        """Signal the listener to stop and wait for remaining records."""
        with self._lock:
            thread = self._thread
            if thread is None:
                return
            if not self._stopping:
                self._stopping = True
                self._queue.put(self._SENTINEL)

        thread.join()
        with self._lock:
            self._thread = None

    def __enter__(self) -> QueueListener:
        self.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.stop()
