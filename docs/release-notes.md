# Release Notes

## 1.2.0

Release date: 2026-05-10

Stdlib-logging bridge plus stdlib-style top-level API so projects can drop `import logging` entirely.

### Added

- `mollog.configure(format=...)` accepts stdlib `%(asctime)s`-style format strings (and `datefmt=`), rendered through the new `StdlibStyleFormatter`.
- `mollog.configure(capture_stdlib=True)` — default — installs a `StdlibBridgeHandler` on stdlib's root logger so third-party libraries that emit through `logging` flow through mollog's hierarchy. Disable with `capture_stdlib=False`.
- `Logger.set_level()` and `BoundLogger.set_level()` accept `Level | str | int`, and propagate to `logging.getLogger(name).setLevel(...)` so noisy libraries are silenced at the source.
- Top-level helpers on the root logger: `mollog.trace`, `mollog.debug`, `mollog.info`, `mollog.warning`, `mollog.error`, `mollog.critical`, `mollog.exception`, `mollog.set_level`.
- Stdlib-compatible level constants: `mollog.TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
- New public surface: `StdlibBridgeHandler`, `StdlibStyleFormatter`, `capture_stdlib_logging`, `release_stdlib_logging`.

### Changed

- `LoggerManager.shutdown()` and `_reset()` also tear down any installed stdlib bridges.

### Breaking changes

None. All additions are backward compatible.

## 1.1.0

Release date: 2026-04-18

### Added

- `configure(filename=...)` now wires up both a `StreamHandler` (terminal) and a `FileHandler` in one call, with `filemode`, `file_level`, `file_formatter`, and `encoding` kwargs.

### Changed

- Promoted `rich` from an optional extra to a required runtime dependency; removed the `[rich]` install extra and lazy-loading scaffolding.

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
