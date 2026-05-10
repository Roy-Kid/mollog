import json
import logging as _stdlib
from abc import ABC, abstractmethod
from typing import Literal

from mollog._record import LogRecord

_RESERVED_FIELDS = {"timestamp", "level", "logger_name", "message", "exception", "stack_info"}


class Formatter(ABC):
    """Base class for log record formatters."""

    @abstractmethod
    def format(self, record: LogRecord) -> str: ...


class TextFormatter(Formatter):
    """Human-readable text formatter.

    Default format: ``YYYY-MM-DD HH:MM:SS.fff | LEVEL    | logger | message``

    Use *template* for custom formats.  Available keys:
    ``timestamp``, ``level``, ``logger_name``, ``message``, ``exception``,
    ``stack_info``, and any extra field.
    """

    def __init__(self, template: str | None = None, datefmt: str = "%Y-%m-%d %H:%M:%S.%f") -> None:
        self._template = template
        self._datefmt = datefmt

    def format(self, record: LogRecord) -> str:
        ts = record.timestamp.strftime(self._datefmt)
        extra_fields = _normalize_extra_fields(record.extra)

        if self._template is not None:
            fields = {
                **extra_fields,
                "timestamp": ts,
                "level": str(record.level),
                "logger_name": record.logger_name,
                "message": record.message,
                "exception": record.exception or "",
                "stack_info": record.stack_info or "",
            }
            return self._template.format_map(fields)

        parts = [ts, f"{record.level!s:<8s}", record.logger_name, record.message]
        line = " | ".join(parts)
        if extra_fields:
            extras = " ".join(f"{k}={v}" for k, v in extra_fields.items())
            line = f"{line} | {extras}"
        if record.exception:
            line = f"{line}\n{record.exception}"
        if record.stack_info:
            line = f"{line}\nStack (most recent call last):\n{record.stack_info}"
        return line


class JSONFormatter(Formatter):
    """Single-line JSON formatter."""

    def format(self, record: LogRecord) -> str:
        data: dict[str, object] = {
            "timestamp": record.timestamp.isoformat(),
            "level": str(record.level),
            "logger_name": record.logger_name,
            "message": record.message,
            **_normalize_extra_fields(record.extra),
        }
        if record.exception:
            data["exception"] = record.exception
        if record.stack_info:
            data["stack_info"] = record.stack_info
        return json.dumps(data, ensure_ascii=False, default=str)


class StdlibStyleFormatter(Formatter):
    """Formatter that accepts stdlib :mod:`logging` ``%(asctime)s``-style format strings.

    Drop-in for users migrating from :func:`logging.basicConfig`. The
    full set of stdlib placeholders is supported because formatting
    delegates to :class:`logging.Formatter` after translating mollog's
    :class:`LogRecord` into a stdlib :class:`logging.LogRecord`.
    """

    def __init__(
        self,
        fmt: str,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
    ) -> None:
        self._fmt = fmt
        self._datefmt = datefmt
        self._style = style
        self._formatter = _stdlib.Formatter(fmt=fmt, datefmt=datefmt, style=style)

    def format(self, record: LogRecord) -> str:
        from mollog._stdlib_bridge import mollog_to_stdlib_level

        std = _stdlib.LogRecord(
            name=record.logger_name,
            level=mollog_to_stdlib_level(record.level),
            pathname="",
            lineno=0,
            msg=record.message,
            args=(),
            exc_info=None,
        )
        std.created = record.timestamp.timestamp()
        std.msecs = (std.created - int(std.created)) * 1000.0
        std.levelname = str(record.level)
        for key, value in record.extra.items():
            if not hasattr(std, key):
                setattr(std, key, value)
        if record.exception:
            std.exc_text = record.exception
        if record.stack_info:
            std.stack_info = record.stack_info
        return self._formatter.format(std)


def _normalize_extra_fields(extra: dict[str, object]) -> dict[str, object]:
    normalized: dict[str, object] = {}
    for key, value in extra.items():
        target = key if key not in _RESERVED_FIELDS else f"extra_{key}"
        normalized[target] = value
    return normalized
