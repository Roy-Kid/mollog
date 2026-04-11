from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Any

_context: ContextVar[dict[str, Any]] = ContextVar("mollog_context", default={})


def get_context() -> dict[str, Any]:
    """Return a copy of the current context-local logging fields."""

    return dict(_context.get())


def bind_context(**extra: Any) -> Token[dict[str, Any]]:
    """Merge fields into the current context-local logging state."""

    merged = get_context()
    merged.update(extra)
    return _context.set(merged)


def reset_context(token: Token[dict[str, Any]]) -> None:
    """Reset the context to a previously returned token."""

    _context.reset(token)


def clear_context() -> None:
    """Remove all current context-local logging fields."""

    _context.set({})


@contextmanager
def scoped_context(**extra: Any) -> Iterator[dict[str, Any]]:
    """Temporarily bind context fields for the active execution context."""

    token = bind_context(**extra)
    try:
        yield get_context()
    finally:
        reset_context(token)
