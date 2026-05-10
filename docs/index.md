# mollog

Structured logging for Python with a stdlib-compatible API — projects can drop `import logging` entirely while keeping access to `%(asctime)s`-style format strings and the third-party library ecosystem that emits through stdlib.

[Get started](getting-started.md){ .md-button .md-button--primary }
[API reference](api.md){ .md-button }

## What it gives you

- Drop-in for `logging.basicConfig`: stdlib-style `format=` strings via `StdlibStyleFormatter`
- Stdlib bridge that captures records from libraries which still use `logging` (httpx, urllib3, openai, …) and routes them through mollog
- Top-level helpers — `mollog.info(...)`, `mollog.warning(...)`, `mollog.set_level(...)` — and `Logger.set_level()` that also propagates to stdlib
- Named loggers with hierarchy and propagation
- Structured `extra` fields and reusable context via `bind()`
- Context-local fields for async and request-scoped flows via `contextvars`
- Exception and stack capture on every record
- Text, JSON, and stdlib-style formatters
- Stream, file, rotating-file, timed-rotating, queue, and null handlers
- Rich console output for local tooling and CLIs
- `configure()` and `shutdown()` helpers for application lifecycle

## Quick example

```python
import mollog

mollog.configure(
    level="INFO",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
mollog.get_logger("httpx").set_level("WARNING")

mollog.info("service booted", port=8080)
```

## Documentation map

- [Getting Started](getting-started.md) — installation, setup, common patterns
- [Configuration](configuration.md) — root logger setup, stdlib bridge, teardown
- [Context Propagation](context.md) — request and task scoped metadata
- [Behavior](behavior.md) — concurrency, reserved fields, shutdown semantics
- [Rich Console](rich.md) — colored terminal output
- [API Reference](api.md) — complete exported surface
