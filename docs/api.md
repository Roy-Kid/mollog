# API Reference

## Top-level helpers

The `mollog` package exposes module-level shortcuts so common workflows can be written without ever importing `logging`.

- `mollog.configure(...)` — root-logger setup; see [Configuration](configuration.md)
- `mollog.basicConfig(**kwargs)` — drop-in for `logging.basicConfig`; accepts stdlib's `filename`, `filemode`, `format`, `datefmt`, `style`, `level`, `stream`, `handlers`, `force`, `encoding`, `errors` kwargs (no-op when the root already has handlers unless `force=True`; `%`-style format strings only) and routes through `configure`
- `mollog.shutdown()` — close handlers, remove stdlib bridges, clear context-local state
- `mollog.get_logger(name="")` — get-or-create a named logger
- `mollog.getLogger(name=None)` — stdlib-compatible alias for `get_logger`; `None` (or `""`) returns the root logger
- `mollog.set_level(level)` — set the root logger's minimum level
- `mollog.trace(message, **extra)`
- `mollog.debug(message, **extra)`
- `mollog.info(message, **extra)`
- `mollog.warning(message, **extra)`
- `mollog.error(message, **extra)`
- `mollog.critical(message, **extra)`
- `mollog.exception(message, **extra)` — captures the current exception via `exc_info=True`

Each level helper also accepts optional `exc_info=` and `stack_info=` keyword arguments.

## Level constants

Level constants are the plain `int` objects re-exported from stdlib `logging`, so `mollog.WARNING is logging.WARNING`. `TRACE` is mollog's superset addition (a plain `int`, value `5`) that stdlib has no equivalent for.

- `mollog.NOTSET`, `mollog.TRACE`, `mollog.DEBUG`, `mollog.INFO`, `mollog.WARNING`, `mollog.WARN`, `mollog.ERROR`, `mollog.CRITICAL`, `mollog.FATAL`

`WARN` and `FATAL` are stdlib's aliases for `WARNING` and `CRITICAL` respectively.

## Core types

### `Level`

Severity enum in ascending order:

- `TRACE` (5), `DEBUG` (10), `INFO` (20), `WARNING` (30), `ERROR` (40), `CRITICAL` (50)

`Level.coerce(value)` parses an enum member, level name string, or stdlib int into a `Level`.

### `LogRecord`

Immutable dataclass with: `level`, `message`, `logger_name`, `timestamp`, `extra`, `exception`, `stack_info`.

## Loggers

### `Logger`

Main entry point for named logging.

Methods:

- `add_handler(handler)`
- `remove_handler(handler)`
- `clear_handlers(close=False)`
- `is_enabled_for(level)`
- `set_level(level)` — accepts `Level | str | int`; also propagates to `logging.getLogger(name).setLevel(...)` so stdlib drops the record at the source
- `trace(message, **extra)`
- `debug(message, **extra)`
- `info(message, **extra)`
- `warning(message, **extra)`
- `error(message, **extra)`
- `critical(message, **extra)`
- `exception(message, **extra)`
- `fire(message, *, level=Level.INFO, **extra)` — dispatch to attached `LogfireHandler`(s) only
- `bind(**extra)` — returns a `Logger` view carrying additional persistent fields
- `close()`

Each level method also accepts optional `exc_info=` and `stack_info=` keyword arguments.

For a stdlib-compatible drop-in, `Logger` also exposes camelCase aliases and helpers with `logging.Logger` semantics: `setLevel`, `addHandler`, `removeHandler`, `isEnabledFor` (aliases of the snake_case methods above), plus `hasHandlers()`, `getEffectiveLevel()`, and `getChild(suffix)`.

## Context helpers

All context operations live on the `Context` namespace class:

- `Context.bind(**extra) -> Token`
- `Context.reset(token) -> None`
- `Context.clear() -> None`
- `Context.get() -> dict`
- `Context.scope(name=None, **extra)` — context manager; also opens a logfire span when `name` is given and logfire is configured

## Logfire integration

- `configure_logfire(*, token=None, service_name=None, send_to_logfire=True, **logfire_kwargs)` — configure the optional logfire backend. Requires `pip install "molcrafts-mollog[logfire]"`. Reads no environment variables; pass all configuration explicitly.
- `LogfireHandler(level=Level.TRACE)` — handler that forwards records to logfire. Attach with `logger.add_handler(LogfireHandler())`; `logger.fire(...)` routes events exclusively through attached `LogfireHandler` instances.

## Handlers

### `Handler`

Abstract base class for handlers. Subclass and implement `emit(record)`; the base provides `set_level`, `set_formatter`, filter management (`add_filter` / `remove_filter` / `clear_filters`), level/filter gating in `handle`, and context-manager support.

### `StreamHandler`

Writes formatted lines to a text stream. Defaults to `sys.stderr`.

### `NullHandler`

Discards all records.

### `FileHandler`

Appends formatted lines to a file.

### `RotatingFileHandler`

Rotates when file size reaches `max_bytes`.

### `TimedRotatingFileHandler`

Rotates after a fixed interval in seconds, minutes, hours, or days.

### `QueueHandler`

Pushes records into a queue for asynchronous fan-out.

### `QueueListener`

Consumes records from a queue and dispatches them to one or more handlers on a background thread.

### `LogfireHandler`

Handler that forwards records to `logfire` (see the Logfire integration section above).

### `StdlibBridgeHandler`

Stdlib `logging.Handler` that converts each incoming `logging.LogRecord` into a mollog `LogRecord` and dispatches it through `LoggerManager().get_logger(record.name)`. Installed by `mollog.configure(capture_stdlib=True)` (the default) on stdlib's root logger.

## Formatters

### `Formatter`

Abstract base class for formatters. Subclass and implement `format(record) -> str`.

### `TextFormatter`

Human-readable formatter with optional string templates.

### `JSONFormatter`

Single-line JSON formatter for structured log pipelines.

### `RichFormatter`

Formatter that produces ANSI-styled lines via `rich`. Pair with any string-writing handler via `handler.set_formatter(RichFormatter())`.

### `StdlibStyleFormatter`

Drop-in for `logging.Formatter`. Accepts stdlib `%(asctime)s`-style format strings; used internally when you pass `format=` to `mollog.configure(...)`.

## Filters

### `Filter`

Abstract base class for record filtering.

### `LevelFilter`

Filters records by `min_level` and `max_level`.

## Utilities

### `Timer`

`Timer(name, *, log=True, level=Level.INFO, logger_name="mollog.timer")` — wall-clock stopwatch backed by `time.perf_counter`. Use it as a context manager (logs `"<name> took <seconds>s"` on exit by default) or drive it explicitly:

- `start()` — start or restart; returns `self` for chaining
- `stop()` — stop, optionally log, and return elapsed seconds
- `elapsed` — elapsed seconds (`0.0` before `start`, live while running)
- `running` — `True` between `start` and `stop`

Pass `log=False` to use it as a silent stopwatch and read `elapsed` yourself.

## Manager helpers

### `LoggerManager`

Singleton registry used for hierarchical logger lookup.

### `get_logger(name="")`

Convenience helper that creates or returns a named logger and ensures a default root stream handler exists.

### `getLogger(name=None)`

Stdlib-compatible alias for `get_logger`. `None` or `""` returns the root logger.

### `configure(...)`

Configures the root logger. Accepts `level`, `handlers`, `formatter` *or* `format` (stdlib `%(asctime)s`-style), `datefmt`, `replace`, `stream`, `filename`, `filemode`, `file_level`, `file_formatter`, `encoding`, and `capture_stdlib`. See [Configuration](configuration.md).

### `basicConfig(**kwargs)`

Drop-in for `logging.basicConfig`. Accepts the stdlib kwargs (`filename`, `filemode`, `format`, `datefmt`, `style`, `level`, `stream`, `handlers`, `force`, `encoding`, `errors`) with stdlib semantics — a no-op when the root logger already has handlers unless `force=True`; `stream` / `filename` / `handlers` are mutually exclusive; only `%`-style format strings are accepted. Routes through `configure`, so the stdlib bridge is installed. Returns `None`.

### `shutdown()`

Closes configured handlers, removes any installed `StdlibBridgeHandler`, and clears context-local runtime state.

## Stdlib bridge helpers

### `capture_stdlib_logging(*, level=Level.TRACE, replace=True)`

Installs a `StdlibBridgeHandler` on stdlib's root logger and returns it. With `replace=True` (default), removes any existing root handlers first, mirroring `logging.basicConfig` reset semantics.

### `release_stdlib_logging()`

Removes every `StdlibBridgeHandler` from stdlib's root logger. Idempotent; leaves other handlers untouched.
