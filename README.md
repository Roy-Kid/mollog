# mollog

[![CI](https://github.com/Roy-Kid/mollog/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/Roy-Kid/mollog/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/molcrafts-mollog.svg)](https://pypi.org/project/molcrafts-mollog/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python](https://img.shields.io/badge/python-3.12%2B-3776AB.svg?logo=python&logoColor=white)](./pyproject.toml)
[![Typed](https://img.shields.io/badge/typing-py.typed-0F766E.svg)](./src/mollog/py.typed)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-16A34A.svg)](./LICENSE)
[![Runtime](https://img.shields.io/badge/runtime-zero%20deps-4F46E5.svg)](#highlights)

`mollog` is a typed, dependency-free structured logging library for Python applications that want clear output, small surface area, and explicit control.

Version `1.0.0` focuses on the pieces needed in real projects: hierarchical loggers, structured context, JSON/text formatting, queue-based fan-out, optional Rich console output, and predictable shutdown/configuration hooks.

## Highlights

- Zero required runtime dependencies
- Typed public API with `py.typed`
- `configure()` and `shutdown()` helpers for application setup
- Structured `extra`, `bind()`, and context-local fields via `bind_context()` / `scoped_context()`
- Text, JSON, file, rotating-file, timed-rotating, queue, and Rich handlers
- Exception and stack capture built into the record model

## Installation

Core package:

```bash
pip install molcrafts-mollog
```

Development environment:

```bash
pip install -e ".[dev,docs,rich]"
```

Rich terminal support:

```bash
pip install "molcrafts-mollog[rich]"
```

## Quickstart

```python
from mollog import JSONFormatter, StreamHandler, configure, get_logger

handler = StreamHandler()
handler.set_formatter(JSONFormatter())
configure(level="info", handlers=[handler])

logger = get_logger("api")
logger.info("request complete", status=200, duration_ms=18)
```

## Contextual logging

```python
from mollog import bind_context, get_logger, scoped_context

logger = get_logger("worker")

with scoped_context(request_id="req-42", trace_id="trace-7"):
    logger.bind(component="ingest").info("started")

token = bind_context(batch="nightly")
try:
    logger.info("continuing")
finally:
    from mollog import reset_context

    reset_context(token)
```

## Exception logging

```python
from mollog import get_logger

logger = get_logger("api")

try:
    raise ValueError("bad payload")
except ValueError:
    logger.exception("request failed", request_id="req-17")
```

## Rich console output

```python
from mollog import RichHandler, configure, get_logger

configure(handlers=[RichHandler()], level="debug")
logger = get_logger("cli")
logger.warning("unexpected value", field="charge", observed="2+")
```

## Release-ready API surface

Core exports include:

- `get_logger()`
- `configure()`
- `shutdown()`
- `bind_context()`
- `scoped_context()`
- `clear_context()`
- `Logger`, `BoundLogger`, `LoggerManager`
- `TextFormatter`, `JSONFormatter`
- `StreamHandler`, `FileHandler`, `RotatingFileHandler`, `TimedRotatingFileHandler`, `QueueHandler`
- `RichHandler` with `molcrafts-mollog[rich]`

## Documentation

The repository includes a Zensical documentation site.

```bash
uv run zensical serve
```

Build the static site:

```bash
uv run zensical build
```

Main pages:

- [Getting Started](docs/getting-started.md)
- [Configuration](docs/configuration.md)
- [Context Propagation](docs/context.md)
- [Behavior Notes](docs/behavior.md)
- [Rich Console Logging](docs/rich.md)
- [API Reference](docs/api.md)
- [Release Notes](docs/release-notes.md)

## Development

```bash
pip install ".[dev]"
pytest -q
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution workflow and [RELEASING.md](RELEASING.md) for the `1.x` release process.
