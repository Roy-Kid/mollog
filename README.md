<div align="center">

<h1>
  <img src=".github/assets/moko.svg" alt="" height="48" align="absmiddle">
  &nbsp;mollog
</h1>

<p><strong>Structured logging for Python with a stdlib-compatible API — no <code>import logging</code> required.</strong></p>

<p>
  <a href="https://github.com/MolCrafts/mollog/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/MolCrafts/mollog/ci.yml?style=flat-square&logo=githubactions&logoColor=white&label=CI" alt="CI"></a>
  <a href="https://pypi.org/project/molcrafts-mollog/"><img src="https://img.shields.io/pypi/v/molcrafts-mollog?style=flat-square&logo=pypi&logoColor=white&label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/molcrafts-mollog/"><img src="https://img.shields.io/pypi/pyversions/molcrafts-mollog?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-BSD--3--Clause-18432B?style=flat-square" alt="License"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square" alt="Ruff"></a>
</p>

<p>
  <a href="https://github.com/MolCrafts/mollog/tree/master/docs"><b>Documentation</b></a> &nbsp;&middot;&nbsp;
  <a href="#quick-start"><b>Quick start</b></a> &nbsp;&middot;&nbsp;
  <a href="#molcrafts-ecosystem"><b>Ecosystem</b></a>
</p>

</div>

mollog is a structured logging library for Python that mirrors the standard library's `logging` API while adding structured `extra` fields, JSON output, context propagation, and a bridge that funnels stdlib records into its own hierarchy. Migrate from `logging.basicConfig` without changing your format strings.

## Capabilities

| Module | Capability |
|--------|------------|
| `_manager` | Singleton logger registry plus the top-level API: `configure` / `basicConfig`, `get_logger` / `getLogger`, `set_level`, `shutdown`, and `trace`/`debug`/`info`/`warning`/`error`/`critical`/`exception` helpers |
| `_logger` | Named `Logger` with hierarchy, propagation, per-logger levels, `bind()` for reusable context, and exception/stack capture |
| `_record` | Immutable frozen `LogRecord` dataclass — level, message, logger name, timestamp, `extra`, exception, stack info |
| `_level` | `Level` enum — `TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` — with coercion from ints, names, or enum values |
| `_context` | `Context` namespace — thread- and asyncio-safe context fields via `contextvars`; `Context.scope()` doubles as a logfire span |
| `_handler` | `Handler` base class plus `StreamHandler` and `NullHandler` |
| `_file_handler` | `FileHandler`, `RotatingFileHandler`, and `TimedRotatingFileHandler` |
| `_queue` | `QueueHandler` and background-thread `QueueListener` for thread/process-safe logging |
| `_formatter` | `Formatter` base plus `TextFormatter`, `JSONFormatter`, and stdlib-style `StdlibStyleFormatter` |
| `_rich` | `RichFormatter` — ANSI-styled, color-coded output via `rich` |
| `_filter` | `Filter` base class and `LevelFilter` for level-range filtering |
| `_stdlib_bridge` | `StdlibBridgeHandler` plus `capture_stdlib_logging` / `release_stdlib_logging` — routes stdlib `logging` records through mollog |
| `_logfire` | Optional `LogfireHandler` and `configure_logfire()` for Pydantic Logfire backends |

## Install

```bash
pip install molcrafts-mollog
# with the optional logfire backend
pip install "molcrafts-mollog[logfire]"
```

Requires Python 3.12+. The only runtime dependency is `rich`.

## Quick start

```python
import mollog

mollog.configure(
    level="INFO",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
mollog.get_logger("httpx").set_level("WARNING")  # silence a noisy library

mollog.info("service booted", port=8080)
```

`mollog.configure(...)` accepts the same `format=` strings as `logging.basicConfig`, and by default installs a bridge so records emitted by libraries that still use stdlib `logging` (httpx, urllib3, openai, …) flow through mollog's hierarchy. Disable with `capture_stdlib=False`.

## Documentation

The full guide lives in [`docs/`](https://github.com/MolCrafts/mollog/tree/master/docs):

- [Getting started](https://github.com/MolCrafts/mollog/blob/master/docs/getting-started.md)
- [Configuration](https://github.com/MolCrafts/mollog/blob/master/docs/configuration.md)
- [Context](https://github.com/MolCrafts/mollog/blob/master/docs/context.md)
- [Behavior](https://github.com/MolCrafts/mollog/blob/master/docs/behavior.md)
- [Rich output](https://github.com/MolCrafts/mollog/blob/master/docs/rich.md)
- [Logfire backend](https://github.com/MolCrafts/mollog/blob/master/docs/logfire.md)
- [API reference](https://github.com/MolCrafts/mollog/blob/master/docs/api.md)

## MolCrafts ecosystem

| Project | Role |
|---------|------|
| [molpy](https://github.com/MolCrafts/molpy)     | Python toolkit — the shared molecular data model & workflow layer |
| [molrs](https://github.com/MolCrafts/molrs)     | Rust core — molecular data structures & compute kernels (native + WASM) |
| [molpack](https://github.com/MolCrafts/molpack) | Packmol-grade molecular packing (Rust + Python) |
| [molvis](https://github.com/MolCrafts/molvis)   | WebGL molecular visualization & editing |
| [molexp](https://github.com/MolCrafts/molexp)   | Workflow & experiment-management platform |
| [molnex](https://github.com/MolCrafts/molnex)   | Molecular machine-learning framework |
| [molq](https://github.com/MolCrafts/molq)       | Unified job queue — local / SLURM / PBS / LSF |
| [molcfg](https://github.com/MolCrafts/molcfg)   | Layered configuration library |
| **mollog**   | Structured logging, stdlib-compatible — this repo |
| [molhub](https://github.com/MolCrafts/molhub)   | Molecular dataset hub |
| [molmcp](https://github.com/MolCrafts/molmcp)   | MCP server for the ecosystem |
| [molrec](https://github.com/MolCrafts/molrec)   | Atomistic record specification |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

BSD-3-Clause — see [LICENSE](LICENSE).

<hr>

<div align="center">
<sub>Crafted with 💚 by <a href="https://github.com/MolCrafts">MolCrafts</a></sub>
</div>
