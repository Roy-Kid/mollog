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
- `bind(**extra)`
- `clear_handlers(close=False)`
- `close()`

Each level method also accepts optional `exc_info=` and `stack_info=` keyword arguments.

### `BoundLogger`

Wrapper that merges pre-bound context into every emitted record.

## Context helpers

- `bind_context(**extra)`
- `reset_context(token)`
- `clear_context()`
- `get_context()`
- `scoped_context(**extra)`

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

Optional handler backed by `rich`. Available after installing `molcrafts-mollog[rich]`.

## Formatters

### `TextFormatter`

Human-readable formatter with optional string templates.

### `JSONFormatter`

Single-line JSON formatter for structured log pipelines.

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
