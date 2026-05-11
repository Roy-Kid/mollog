# Changelog

## 1.2.2 - 2026-05-11

### Added
- Stdlib drop-in surface so `import mollog as logging` works:
  - `mollog.basicConfig(**kwargs)` accepts stdlib's `filename`, `filemode`, `format`, `datefmt`, `style`, `level`, `stream`, `handlers`, `force`, `encoding`, `errors` kwargs with stdlib semantics (no-op when root has handlers unless `force=True`; mutually exclusive `stream`/`filename`/`handlers`; only `%`-style format strings are accepted).
  - `mollog.getLogger(name=None)` returns the root logger when called with no arg or `None`, otherwise delegates to `get_logger`.
  - `Logger` gains `setLevel`, `addHandler`, `removeHandler`, `isEnabledFor` aliases pointing at the existing snake_case methods, plus `hasHandlers()`, `getEffectiveLevel()`, and `getChild(suffix)` with stdlib semantics.
- Level constants `NOTSET`, `WARN`, `FATAL` re-exported at the top level.

### Changed
- Top-level level constants (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, …) are now the plain-`int` objects from `logging`, so `mollog.WARNING is logging.WARNING`. `TRACE` is mollog's superset addition (still a plain `int`, still coerces back to `Level.TRACE` via `Level.coerce`).

## 1.2.1 - 2026-05-10

### Performance
- Tightened hot paths in `_formatter.py`, `_manager.py`, and `_stdlib_bridge.py`: `mollog.info(...)` and other root-logger helpers no longer acquire a lock on every call once the manager has been configured; `_stdlib_record_extras` short-circuits to a shared empty dict when no user fields are attached to a stdlib record; `StdlibStyleFormatter.format` writes user extras through `record.__dict__` directly instead of a per-attr `hasattr` lookup; collapsed the six near-identical `trace`/`debug`/.../`critical` module-level wrappers into a `_root_proxy` factory. No public API or behavior changes.

## 1.2.0 - 2026-05-10

### Added
- `mollog.configure(format="%(asctime)s %(levelname)s %(name)s %(message)s")` accepts stdlib `logging.basicConfig`-style format strings, plus a matching `datefmt=` kwarg, rendered via the new `StdlibStyleFormatter`.
- `mollog.configure(capture_stdlib=True)` (default) installs a `StdlibBridgeHandler` on stdlib's root logger so third-party libraries that emit through `logging` (httpx, urllib3, …) flow through mollog's hierarchy. Disable with `capture_stdlib=False`.
- `Logger.set_level()` accepts `Level | str | int` and propagates to `logging.getLogger(name).setLevel(...)` so per-logger silencing applies at both layers.
- Module-level convenience helpers on the root logger: `mollog.trace`, `mollog.debug`, `mollog.info`, `mollog.warning`, `mollog.error`, `mollog.critical`, `mollog.exception`, `mollog.set_level`.
- Stdlib-compatible level constants re-exported at the top level: `mollog.TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
- New public surface: `StdlibBridgeHandler`, `StdlibStyleFormatter`, `capture_stdlib_logging`, `release_stdlib_logging`.

### Changed
- `LoggerManager.shutdown()` and `_reset()` also tear down any installed stdlib bridges.

## 1.1.0 - 2026-04-18

### Added
- `configure(filename=...)` now wires up both a StreamHandler (terminal) and a FileHandler in one call, with `filemode`, `file_level`, `file_formatter`, and `encoding` kwargs.

### Changed
- Promoted `rich` from an optional extra to a required runtime dependency; removed the `[rich]` install extra and lazy-loading scaffolding.

## 1.0.0 - 2026-04-11

Initial stable release.

### Added

- thread-safe logger and logger-manager mutation paths
- `RichHandler` behind optional `mollog[rich]`
- exception and stack logging via `exc_info`, `stack_info`, and `logger.exception(...)`
- context-local structured fields via `bind_context()`, `scoped_context()`, and related helpers
- top-level `configure()` and `shutdown()` helpers for application setup and teardown
- Zensical documentation site, API guide, behavior notes, and Rich usage guide
- packaging, build, and release workflows for GitHub Actions

### Changed

- reserved formatter fields are protected from `extra` collisions
- queue listener shutdown now drains late-arriving records briefly before exit
- rotating handlers validate invalid configuration eagerly

### Verification

- full test suite passing
- package build and `twine check`
- Zensical site build
