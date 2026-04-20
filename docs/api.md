# API Reference

## Core types

### `Level`

Severity enum in ascending order:

- `TRACE`
- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

Also provides `Level.coerce(...)` for configuration-friendly parsing from enum values, strings, or ints.

### `LogRecord`

Immutable dataclass with:

- `level`
- `message`
- `logger_name`
- `timestamp`
- `extra`
- `exception`
- `stack_info`

## Loggers

### `Logger`

Main entry point for named logging.

Methods:

- `add_handler(handler)`
- `remove_handler(handler)`
- `is_enabled_for(level)`
- `trace(message, **extra)`
- `debug(message, **extra)`
- `info(message, **extra)`
- `warning(message, **extra)`
- `error(message, **extra)`
- `critical(message, **extra)`
- `exception(message, **extra)`
- `fire(message, *, level=Level.INFO, **extra)` — dispatch to attached `LogfireHandler`(s) only
- `bind(**extra)` — returns a `Logger` view carrying additional persistent fields
- `clear_handlers(close=False)`
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

## Formatters

### `TextFormatter`

Human-readable formatter with optional string templates.

### `JSONFormatter`

Single-line JSON formatter for structured log pipelines.

### `RichFormatter`

Formatter that produces ANSI-styled lines via `rich`. Pair with any string-writing handler via `handler.set_formatter(RichFormatter())`.

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

Configures the root logger with explicit handlers, level, and optional formatter.

### `shutdown()`

Closes configured handlers and clears context-local runtime state.
