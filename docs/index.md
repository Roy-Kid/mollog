# mollog

Zero-dependency structured logging for Python applications that need clear output, a small surface area, and explicit control.

[Get started](getting-started.md){ .md-button .md-button--primary }
[API reference](api.md){ .md-button }

## What it gives you

- Named loggers with hierarchy and propagation
- Structured `extra` fields and reusable context via `bind()`
- Context-local fields for async and request-scoped flows via `contextvars`
- Exception and stack capture on every record
- Text and JSON formatters
- Stream, file, rotating-file, timed-rotating, queue, and null handlers
- Optional Rich console output for local tooling and CLIs
- `configure()` and `shutdown()` helpers for application lifecycle
- No runtime dependencies

## Quick example

```python
from mollog import JSONFormatter, StreamHandler, configure, get_logger

handler = StreamHandler()
handler.set_formatter(JSONFormatter())
configure(level="info", handlers=[handler])

logger = get_logger("api")
logger.info("request complete", status=200, duration_ms=18)
```

## Documentation map

- [Getting Started](getting-started.md) — installation, setup, common patterns
- [Configuration](configuration.md) — root logger setup and teardown
- [Context Propagation](context.md) — request and task scoped metadata
- [Behavior](behavior.md) — concurrency, reserved fields, shutdown semantics
- [Rich Console](rich.md) — colored terminal output
- [API Reference](api.md) — complete exported surface
