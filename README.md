# mollog

[![CI](https://github.com/MolCrafts/mollog/actions/workflows/ci.yml/badge.svg)](https://github.com/MolCrafts/mollog/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/molcrafts-mollog.svg)](https://pypi.org/project/molcrafts-mollog/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python](https://img.shields.io/badge/python-3.12%2B-3776AB.svg?logo=python&logoColor=white)](./pyproject.toml)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-16A34A.svg)](./LICENSE)

Zero-dependency structured logging for Python.

## Quick Start

```python
from mollog import JSONFormatter, StreamHandler, configure, get_logger

handler = StreamHandler()
handler.set_formatter(JSONFormatter())
configure(level="info", handlers=[handler])

logger = get_logger("api")
logger.info("request complete", status=200, duration_ms=18)
```

```bash
pip install molcrafts-mollog
# with Rich terminal output
pip install "molcrafts-mollog[rich]"
```

## Features

- Named loggers with hierarchy and propagation
- Structured `extra` fields and `bind()` for reusable context
- Context-local fields via `bind_context()` / `scoped_context()`
- Exception and stack capture on every record
- `TextFormatter` and `JSONFormatter`
- `StreamHandler`, `FileHandler`, `RotatingFileHandler`, `TimedRotatingFileHandler`, `QueueHandler`
- Optional `RichHandler` for colored terminal output
- `configure()` and `shutdown()` for application lifecycle
- No runtime dependencies

---

Built with love by [MolCrafts](https://github.com/MolCrafts)
