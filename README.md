# mollog

[![CI](https://github.com/MolCrafts/mollog/actions/workflows/ci.yml/badge.svg)](https://github.com/MolCrafts/mollog/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/molcrafts-mollog.svg)](https://pypi.org/project/molcrafts-mollog/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python](https://img.shields.io/badge/python-3.12%2B-3776AB.svg?logo=python&logoColor=white)](./pyproject.toml)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-16A34A.svg)](./LICENSE)

Structured logging for Python with a stdlib-compatible API — no `import logging` required.

## Quick Start

```python
import mollog

mollog.configure(
    level="INFO",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
mollog.get_logger("httpx").set_level("WARNING")  # silence noisy library

mollog.info("service booted", port=8080)
```

`mollog.configure(...)` accepts the same `format=` strings as `logging.basicConfig`, and by default installs a bridge so records emitted by libraries that still use stdlib `logging` (httpx, urllib3, openai, …) flow through mollog's hierarchy. Disable with `capture_stdlib=False`.

```bash
pip install molcrafts-mollog
# with optional logfire backend
pip install "molcrafts-mollog[logfire]"
```

## Features

- Drop-in for `logging.basicConfig`: stdlib-style `format=` strings and stdlib bridge
- Top-level helpers: `mollog.{trace, debug, info, warning, error, critical, exception}`
- Per-logger level control: `mollog.get_logger("httpx").set_level("WARNING")` (propagates to stdlib)
- Named loggers with hierarchy and propagation
- Structured `extra` fields and `Logger.bind()` for reusable context
- Context-local fields via the `Context` namespace (`Context.scope(...)` doubles as a logfire span)
- Exception and stack capture on every record
- `TextFormatter`, `JSONFormatter`, `RichFormatter`, and stdlib-style `StdlibStyleFormatter`
- `StreamHandler`, `FileHandler`, `RotatingFileHandler`, `TimedRotatingFileHandler`, `QueueHandler`
- Optional `LogfireHandler` + `configure_logfire()` for [Pydantic Logfire](https://logfire.pydantic.dev) backends
- `configure()` and `shutdown()` for application lifecycle

---

Built with love by [MolCrafts](https://github.com/MolCrafts)
