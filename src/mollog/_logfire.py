"""Optional :mod:`logfire` backend.

Activated by :func:`mollog.configure_logfire` + attaching a
:class:`LogfireHandler` to a logger. Only this module imports
``logfire``; the rest of mollog keeps logfire as a soft dependency.

No environment variables are read. All configuration must flow through
:func:`configure_logfire` keyword arguments.
"""

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from typing import Any

from mollog._handler import Handler
from mollog._level import Level
from mollog._record import LogRecord

try:  # pragma: no cover - exercised via import fallback in tests
    import logfire as _logfire_mod
except ImportError:  # pragma: no cover
    _logfire_mod = None

_CONFIGURED: bool = False

_LEVEL_MAP: dict[Level, str] = {
    Level.TRACE: "trace",
    Level.DEBUG: "debug",
    Level.INFO: "info",
    Level.WARNING: "warn",
    Level.ERROR: "error",
    Level.CRITICAL: "fatal",
}

_INSTALL_HINT = (
    "logfire is not installed. Install it with: pip install 'molcrafts-mollog[logfire]'"
)
_UNCONFIGURED_HINT = "call mollog.configure_logfire(...) before using logfire features"


def configure_logfire(
    *,
    token: str | None = None,
    service_name: str | None = None,
    send_to_logfire: bool = True,
    **logfire_kwargs: Any,
) -> None:
    """Configure the logfire backend.

    Thin wrapper around :func:`logfire.configure` that refuses to rely on
    environment variables — every setting must be passed as a keyword
    argument. Pass ``send_to_logfire=False`` to run offline.
    """

    if _logfire_mod is None:
        raise ImportError(_INSTALL_HINT)

    global _CONFIGURED
    _logfire_mod.configure(
        token=token,
        service_name=service_name,
        send_to_logfire=send_to_logfire,
        **logfire_kwargs,
    )
    _CONFIGURED = True


def is_configured() -> bool:
    """Return whether :func:`configure_logfire` has been called."""

    return _CONFIGURED


class LogfireHandler(Handler):
    """Forward log records to :mod:`logfire`.

    Attach with ``logger.add_handler(LogfireHandler())``. Requires
    :func:`configure_logfire` to have been called first. When attached,
    every record dispatched to the logger (``logger.info`` etc.) also
    reaches logfire. :meth:`Logger.fire` additionally routes records
    *only* through ``LogfireHandler`` instances, bypassing other
    handlers on the logger chain.
    """

    def __init__(self, level: Level = Level.TRACE) -> None:
        super().__init__(level)

    def emit(self, record: LogRecord) -> None:
        if _logfire_mod is None:
            raise ImportError(_INSTALL_HINT)
        if not _CONFIGURED:
            raise RuntimeError(_UNCONFIGURED_HINT)

        attributes = dict(record.extra)
        if record.logger_name:
            attributes.setdefault("logger_name", record.logger_name)
        _logfire_mod.log(
            _LEVEL_MAP[record.level],
            record.message,
            attributes=attributes,
        )


def open_span(name: str, attributes: dict[str, Any]) -> AbstractContextManager[Any]:
    """Return a context manager that opens a logfire span, or a no-op if unconfigured.

    Used by :meth:`mollog.Context.scope`. We deliberately return a
    :func:`contextlib.nullcontext` when logfire isn't ready so callers
    don't have to special-case the degraded path.
    """

    if _logfire_mod is None or not _CONFIGURED:
        return nullcontext()
    return _logfire_mod.span(name, **attributes)
