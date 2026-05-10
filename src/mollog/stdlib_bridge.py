"""Bridge stdlib :mod:`logging` records into mollog's hierarchy.

When a project mixes mollog with libraries that emit through stdlib
``logging`` (httpx, urllib3, openai, …), :func:`capture_stdlib_logging`
installs a single :class:`StdlibBridgeHandler` on stdlib's root logger
that converts each record into a mollog :class:`LogRecord` and dispatches
it through the matching mollog logger. Combined with
:meth:`mollog.Logger.set_level`, this lets the user silence noisy
third-party loggers without ever importing :mod:`logging`.
"""

from __future__ import annotations

import logging as _stdlib
from datetime import datetime, timezone
from typing import Any

from mollog.level import Level

__all__ = [
    "StdlibBridgeHandler",
    "capture_stdlib_logging",
    "release_stdlib_logging",
    "stdlib_to_mollog_level",
    "mollog_to_stdlib_level",
]


def stdlib_to_mollog_level(levelno: int) -> Level:
    """Map a stdlib numeric level into the closest :class:`Level`."""

    if levelno >= _stdlib.CRITICAL:
        return Level.CRITICAL
    if levelno >= _stdlib.ERROR:
        return Level.ERROR
    if levelno >= _stdlib.WARNING:
        return Level.WARNING
    if levelno >= _stdlib.INFO:
        return Level.INFO
    if levelno >= _stdlib.DEBUG:
        return Level.DEBUG
    return Level.TRACE


_MOLLOG_TO_STDLIB: dict[Level, int] = {
    Level.TRACE: _stdlib.DEBUG,
    Level.DEBUG: _stdlib.DEBUG,
    Level.INFO: _stdlib.INFO,
    Level.WARNING: _stdlib.WARNING,
    Level.ERROR: _stdlib.ERROR,
    Level.CRITICAL: _stdlib.CRITICAL,
}


def mollog_to_stdlib_level(level: Level) -> int:
    """Map a :class:`Level` to its closest stdlib numeric level."""

    return _MOLLOG_TO_STDLIB[level]


_RESERVED_STDLIB_ATTRS = frozenset(
    {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
        "asctime",
    }
)


def _stdlib_record_extras(record: _stdlib.LogRecord) -> dict[str, Any]:
    """Extract user-set extras from a stdlib record.

    Stdlib's ``extra=`` kwarg attaches arbitrary keys directly to the
    record. We forward anything that isn't a known stdlib attribute so
    structured fields survive the bridge.
    """

    return {
        key: value
        for key, value in record.__dict__.items()
        if key not in _RESERVED_STDLIB_ATTRS and not key.startswith("_")
    }


class StdlibBridgeHandler(_stdlib.Handler):
    """Forward stdlib ``logging`` records into the mollog hierarchy.

    The handler is normally installed on stdlib's root logger by
    :func:`capture_stdlib_logging` (called automatically by
    :func:`mollog.configure` unless ``capture_stdlib=False``). Each
    incoming record is translated into a mollog record and dispatched
    through ``LoggerManager().get_logger(record.name)`` so per-logger
    levels set via :meth:`mollog.Logger.set_level` apply uniformly.
    """

    def __init__(self, level: int = _stdlib.NOTSET) -> None:
        super().__init__(level=level)

    def emit(self, record: _stdlib.LogRecord) -> None:  # noqa: D401 - stdlib API
        # Lazy import to avoid a circular dependency at module load time.
        from mollog.manager import LoggerManager

        try:
            level = stdlib_to_mollog_level(record.levelno)
            mollog_logger = LoggerManager().get_logger(record.name)
            if not mollog_logger.is_enabled_for(level):
                return

            try:
                message = record.getMessage()
            except Exception:  # pragma: no cover - defensive: bad % args
                message = str(record.msg)

            extras = _stdlib_record_extras(record)
            timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc)

            from mollog.record import LogRecord as _MolRecord

            exception = self.format_exception(record)
            stack_info = record.stack_info if record.stack_info else None

            mol_record = _MolRecord(
                level=level,
                message=message,
                logger_name=record.name,
                timestamp=timestamp,
                extra=extras,
                exception=exception,
                stack_info=stack_info,
            )
            mollog_logger._dispatch(mol_record)
        except Exception:  # pragma: no cover
            self.handleError(record)

    @staticmethod
    def format_exception(record: _stdlib.LogRecord) -> str | None:
        """Render ``record.exc_info`` into a string, if present."""

        if not record.exc_info:
            return None
        import traceback

        return "".join(traceback.format_exception(*record.exc_info)).rstrip()


def capture_stdlib_logging(
    *,
    level: Level | str | int = Level.TRACE,
    replace: bool = True,
) -> StdlibBridgeHandler:
    """Install a :class:`StdlibBridgeHandler` on stdlib's root logger.

    Parameters
    ----------
    level:
        Minimum level retained at the *stdlib* root before the bridge
        sees the record. Default :data:`Level.TRACE` so mollog's own
        per-logger levels do all the filtering.
    replace:
        When ``True`` (the default), any handlers already installed on
        stdlib's root logger are removed first, including older
        bridges. This mirrors the reset semantics of
        :func:`logging.basicConfig` and prevents records from showing
        up twice (once from stdlib's default handler, once from the
        bridge).

    Returns
    -------
    StdlibBridgeHandler
        The handler that was installed; keep a reference if you intend
        to call :func:`release_stdlib_logging` for fine-grained removal.
    """

    resolved = Level.coerce(level)
    bridge = StdlibBridgeHandler(level=mollog_to_stdlib_level(resolved))

    root = _stdlib.getLogger()
    if replace:
        for existing in tuple(root.handlers):
            root.removeHandler(existing)
            try:
                existing.close()
            except Exception:  # pragma: no cover - defensive
                pass
    else:
        for existing in tuple(root.handlers):
            if isinstance(existing, StdlibBridgeHandler):
                root.removeHandler(existing)

    root.addHandler(bridge)
    # Stdlib's root defaults to WARNING, which would silently drop INFO
    # records before our bridge ever sees them. Lower it to NOTSET so
    # mollog's hierarchy gets to make the level decision.
    root.setLevel(_stdlib.NOTSET)
    return bridge


def release_stdlib_logging() -> None:
    """Remove every :class:`StdlibBridgeHandler` from stdlib's root logger.

    Idempotent: a no-op when no bridges are installed. Other handlers
    on the stdlib root are left untouched.
    """

    root = _stdlib.getLogger()
    for handler in tuple(root.handlers):
        if isinstance(handler, StdlibBridgeHandler):
            root.removeHandler(handler)
            try:
                handler.close()
            except Exception:  # pragma: no cover - defensive
                pass
