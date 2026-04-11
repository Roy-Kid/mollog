# Behavior And Guarantees

## Logger and manager concurrency

`Logger.add_handler()`, `Logger.remove_handler()`, and logger dispatch now take snapshots of handler state before iterating. `LoggerManager` also serializes logger creation and default-root configuration so first-use races don't produce duplicate loggers or duplicate default handlers.

## Reserved formatter fields

Core record fields are protected:

- `timestamp`
- `level`
- `logger_name`
- `message`

If user-supplied `extra` data reuses one of these keys, the field is renamed with an `extra_` prefix in formatter output.

Examples:

- `{"message": "shadow"}` becomes `extra_message`
- `{"level": "DEBUG"}` becomes `extra_level`

This preserves the original record shape and avoids silent overwrites.

## Optional Rich support

`RichHandler` lives behind the `molcrafts-mollog[rich]` extra. Importing `mollog` does not require `rich`; the optional dependency is loaded only when `RichHandler` is accessed.

## Exception logging

Records can now carry two additional diagnostic fields:

- `exception`
- `stack_info`

`logger.exception("...")` is a shortcut for `logger.error("...", exc_info=True)`.

All built-in formatters and handlers understand these fields:

- `TextFormatter` appends traceback and stack blocks after the main log line
- `JSONFormatter` emits `exception` and `stack_info` keys
- `RichHandler` prints the main record first, then the traceback and stack output

## Context-local metadata

Context fields are stored with `contextvars`, so they follow the current execution context rather than using a mutable process-global dictionary.

Per-record merge precedence is:

1. context-local fields
2. bound logger fields
3. per-call extra fields

This keeps request-scoped metadata implicit while still allowing explicit per-call overrides.

## Queue listener shutdown

`QueueListener.stop()` now uses a short drain window after receiving its stop sentinel. That improves the common race where a small number of records arrive just after shutdown begins.

This is still not a substitute for coordinated shutdown. Production code should stop producers before stopping the listener.

## Rotation semantics

Rotating handlers validate their configuration early:

- `max_bytes` must be greater than `0`
- `interval` must be greater than `0`
- `backup_count` must be greater than or equal to `0`

When `backup_count=0`, rotation discards the old segment and starts a fresh file instead of creating archives.
