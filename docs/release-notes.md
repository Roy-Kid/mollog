# Release Notes

## 1.2.2

Release date: 2026-05-11

Completes the stdlib drop-in surface so `import mollog as logging` works.

### Added

- `mollog.basicConfig(**kwargs)` accepts stdlib's `filename`, `filemode`, `format`, `datefmt`, `style`, `level`, `stream`, `handlers`, `force`, `encoding`, `errors` kwargs with stdlib semantics (no-op when the root has handlers unless `force=True`; mutually exclusive `stream` / `filename` / `handlers`; only `%`-style format strings are accepted).
- `mollog.getLogger(name=None)` returns the root logger when called with no argument or `None`, otherwise delegates to `get_logger`.
- `Logger` gains `setLevel`, `addHandler`, `removeHandler`, `isEnabledFor` aliases for the existing snake_case methods, plus `hasHandlers()`, `getEffectiveLevel()`, and `getChild(suffix)` with stdlib semantics.
- Level constants `NOTSET`, `WARN`, `FATAL` re-exported at the top level.

### Changed

- Top-level level constants (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, …) are now the plain-`int` objects from stdlib `logging`, so `mollog.WARNING is logging.WARNING`. `TRACE` remains mollog's superset addition (still a plain `int`).

### Breaking changes

None. All additions are backward compatible.

## 1.2.1

Release date: 2026-05-10

### Performance

- Tightened hot paths in `_formatter.py`, `_manager.py`, and `_stdlib_bridge.py`: root-logger helpers no longer acquire a lock on every call once the manager has been configured, and stdlib records without user fields short-circuit to a shared empty dict. No public API or behavior changes.

## 1.2.0

Release date: 2026-05-10

Stdlib-logging bridge plus stdlib-style top-level API so projects can drop `import logging` entirely.

### Added

- `mollog.configure(format=...)` accepts stdlib `%(asctime)s`-style format strings (and `datefmt=`), rendered through the new `StdlibStyleFormatter`.
- `mollog.configure(capture_stdlib=True)` — default — installs a `StdlibBridgeHandler` on stdlib's root logger so third-party libraries that emit through `logging` flow through mollog's hierarchy. Disable with `capture_stdlib=False`.
- `Logger.set_level()` accepts `Level | str | int`, and propagates to `logging.getLogger(name).setLevel(...)` so noisy libraries are silenced at the source.
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
- Pydantic Logfire integration: `LogfireHandler`, `configure_logfire(...)`, `Logger.fire(...)`.
- New `Context` namespace replaces the function-based context API; `Context.scope(name, **attrs)` doubles as a logfire span.
- `RichFormatter` (replaces the previous `RichHandler` shape).
- Underscore-prefixed internal modules (`_formatter`, `_handler`, `_logger`, …) — public API is unchanged from prior versions where the export still exists.

### Changed

- Promoted `rich` from an optional extra to a required runtime dependency.

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
