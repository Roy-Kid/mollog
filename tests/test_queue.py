import io
import multiprocessing
import queue as queue_mod

import pytest

from mollog.handler import StreamHandler
from mollog.level import Level
from mollog.queue import QueueHandler, QueueListener
from mollog.record import LogRecord


def _rec(msg: str = "hi") -> LogRecord:
    return LogRecord(level=Level.INFO, message=msg, logger_name="t")


class TestQueueHandlerListener:
    def test_thread_queue(self):
        q: queue_mod.Queue[object] = queue_mod.Queue()
        buf = io.StringIO()
        handler = StreamHandler(stream=buf)
        qh = QueueHandler(q)
        with QueueListener(q, handler):
            qh.handle(_rec("threaded"))
        assert "threaded" in buf.getvalue()

    def test_context_manager(self):
        q: queue_mod.Queue[object] = queue_mod.Queue()
        buf = io.StringIO()
        handler = StreamHandler(stream=buf)
        with QueueListener(q, handler) as listener:
            assert listener._thread is not None
        assert listener._thread is None

    def test_multiple_records(self):
        q: queue_mod.Queue[object] = queue_mod.Queue()
        buf = io.StringIO()
        handler = StreamHandler(stream=buf)
        qh = QueueHandler(q)
        with QueueListener(q, handler):
            for i in range(50):
                qh.handle(_rec(f"msg-{i}"))
        out = buf.getvalue()
        for i in range(50):
            assert f"msg-{i}" in out

    def test_stop_drains_records_after_sentinel(self):
        q: queue_mod.Queue[object] = queue_mod.Queue()
        buf = io.StringIO()
        handler = StreamHandler(stream=buf)
        listener = QueueListener(q, handler, stop_grace_period=0.01)

        listener.start()
        q.put(listener._SENTINEL)
        q.put(_rec("after-stop"))
        assert listener._thread is not None
        listener._thread.join()

        assert "after-stop" in buf.getvalue()

    def test_start_twice_raises(self):
        q: queue_mod.Queue[object] = queue_mod.Queue()
        listener = QueueListener(q)
        listener.start()
        try:
            with pytest.raises(RuntimeError):
                listener.start()
        finally:
            listener.stop()


def _worker(q: multiprocessing.Queue, n: int) -> None:  # type: ignore[type-arg]
    """Worker function for multiprocess test."""
    from mollog.level import Level
    from mollog.queue import QueueHandler
    from mollog.record import LogRecord

    qh = QueueHandler(q)
    for i in range(n):
        rec = LogRecord(level=Level.INFO, message=f"proc-{i}", logger_name="worker")
        qh.handle(rec)


class TestMultiprocess:
    def test_multiprocess_queue(self, tmp_path):
        from mollog.file_handler import FileHandler

        q: multiprocessing.Queue[object] = multiprocessing.Queue()
        log_file = tmp_path / "mp.log"
        fh = FileHandler(log_file)
        msgs_per_proc = 25
        num_procs = 4

        with QueueListener(q, fh):
            procs = []
            for _ in range(num_procs):
                p = multiprocessing.Process(target=_worker, args=(q, msgs_per_proc))
                p.start()
                procs.append(p)
            for p in procs:
                p.join()

        fh.close()
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == num_procs * msgs_per_proc
