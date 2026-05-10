# API Reference

## Top-level helpers

The `mollog` package exposes module-level shortcuts so common workflows can be written without ever importing `logging`.

- `mollog.configure(...)` — root-logger setup; see [Configuration](configuration.md)
- `mollog.shutdown()` — close handlers, remove stdlib bridges, clear context-local state
- `mollog.get_logger(name="")` — get-or-create a named logger
- `mollog.close_logger(name)` — drop a named logger from the registry and close its handlers
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
- `bind(**extra)` — returns a `BoundLogger`
- `close()`

Each level method also accepts optional `exc_info=` and `stack_info=` keyword arguments. `Logger` is a context manager: leaving the `with` block closes its handlers.

### `BoundLogger`

Wrapper that merges pre-bound context into every emitted record. Same methods as `Logger`, plus `bind(**extra)` to layer additional fields. Also a context manager.

## Context helpers

- `bind_context(**extra)`
- `reset_context(token)`
- `clear_context()`
- `get_context()`
- `scoped_context(**extra)` — context manager that binds and unwinds in one block

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

### `RichHandler`

Handler backed by `rich`, available out of the box (rich is a required runtime dependency).

### `StdlibBridgeHandler`

Stdlib `logging.Handler` that converts each incoming `logging.LogRecord` into a mollog `LogRecord` and dispatches it through `LoggerManager().get_logger(record.name)`. Installed by `mollog.configure(capture_stdlib=True)` (the default) on stdlib's root logger.

## Formatters

### `TextFormatter`

Human-readable formatter with optional `{key}` string templates.

### `JSONFormatter`

Single-line JSON formatter for structured log pipelines.

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

### `close_logger(name)`

Drops a named logger from the registry and closes its handlers. Idempotent.

## Stdlib bridge helpers

### `capture_stdlib_logging(*, level=Level.TRACE, replace=True)`

Installs a `StdlibBridgeHandler` on stdlib's root logger and returns it. With `replace=True` (default), removes any existing root handlers first, mirroring `logging.basicConfig` reset semantics.

### `release_stdlib_logging()`

Removes every `StdlibBridgeHandler` from stdlib's root logger. Idempotent; leaves other handlers untouched.
