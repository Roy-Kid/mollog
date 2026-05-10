# API Reference

## Top-level helpers

The `mollog` package exposes module-level shortcuts so common workflows can be written without ever importing `logging`.

- `mollog.configure(...)` — root-logger setup; see [Configuration](configuration.md)
- `mollog.shutdown()` — close handlers, remove stdlib bridges, clear context-local state
- `mollog.get_logger(name="")` — get-or-create a named logger
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

Stdlib-compatible aliases for the `Level` enum members:

- `mollog.TRACE`, `mollog.DEBUG`, `mollog.INFO`, `mollog.WARNING`, `mollog.ERROR`, `mollog.CRITICAL`

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

## Manager helpers

### `LoggerManager`

Singleton registry used for hierarchical logger lookup.

### `get_logger(name="")`

Convenience helper that creates or returns a named logger and ensures a default root stream handler exists.

### `configure(...)`

Configures the root logger. Accepts `level`, `handlers`, `formatter` *or* `format` (stdlib `%(asctime)s`-style), `datefmt`, `replace`, `stream`, `filename`, `filemode`, `file_level`, `file_formatter`, `encoding`, and `capture_stdlib`. See [Configuration](configuration.md).

### `shutdown()`

Closes configured handlers, removes any installed `StdlibBridgeHandler`, and clears context-local runtime state.

## Stdlib bridge helpers

### `capture_stdlib_logging(*, level=Level.TRACE, replace=True)`

Installs a `StdlibBridgeHandler` on stdlib's root logger and returns it. With `replace=True` (default), removes any existing root handlers first, mirroring `logging.basicConfig` reset semantics.

### `release_stdlib_logging()`

Removes every `StdlibBridgeHandler` from stdlib's root logger. Idempotent; leaves other handlers untouched.
