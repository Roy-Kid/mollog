# Release Notes

## 1.0.0

Release date: 2026-04-12

First stable release.

### What's included

- Thread-safe logger and manager operations
- `configure()` and `shutdown()` helpers for application lifecycle
- Structured `extra` fields and `bind()` for reusable logger context
- Context-local fields via `contextvars`: `bind_context()`, `scoped_context()`, `reset_context()`
- Exception and stack capture: `exc_info=`, `stack_info=`, `logger.exception(...)`
- `TextFormatter` and `JSONFormatter`
- `StreamHandler`, `FileHandler`, `RotatingFileHandler`, `TimedRotatingFileHandler`, `QueueHandler`, `NullHandler`
- `QueueListener` with drain window on shutdown
- Optional `RichHandler` behind `molcrafts-mollog[rich]`

### Breaking changes

None — this is the initial stable release.
