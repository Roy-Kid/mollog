from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from mollog.level import Level


@dataclass(frozen=True, slots=True)
class LogRecord:
    """Immutable log entry."""

    level: Level
    message: str
    logger_name: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    extra: dict[str, Any] = field(default_factory=dict)
    exception: str | None = None
    stack_info: str | None = None
