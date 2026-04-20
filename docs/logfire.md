# Logfire Integration

`mollog` can forward structured events to
[pydantic-logfire](https://logfire.pydantic.dev) as an optional backend.
Install the extra to pull it in:

```bash
pip install "molcrafts-mollog[logfire]"
```

## Configuration

`configure_logfire(...)` is a thin wrapper around `logfire.configure(...)`.
It reads **no environment variables** — every setting must be passed
explicitly as a keyword argument:

```python
import mollog

mollog.configure_logfire(
    token="your-write-token",
    service_name="my-api",
)
```

Pass `send_to_logfire=False` to run offline:

```python
mollog.configure_logfire(token=None, send_to_logfire=False, service_name="dev")
```

Any other keyword you pass is forwarded verbatim to `logfire.configure`.

## Attaching `LogfireHandler`

Logfire is exposed as a regular `Handler`. To route records to logfire,
attach a `LogfireHandler` to the relevant logger (typically the root, so
every child logger inherits it via propagation):

```python
import mollog

mollog.configure_logfire(token="...")
root = mollog.get_logger("")
root.add_handler(mollog.LogfireHandler())

logger = mollog.get_logger("api")
logger.info("served")            # stderr (default handler) + logfire
logger.warning("slow query", ms=2300)
```

`LogfireHandler.emit` calls `logfire.log(level, message, attributes=extra)`.
If `configure_logfire` has not been called, emit raises `RuntimeError`;
if the `logfire` package is not installed, it raises `ImportError`.

## `logger.fire` — logfire-only dispatch

`logger.fire(message, *, level=Level.INFO, **extra)` dispatches the
record **only** to `LogfireHandler` instances on the logger chain,
bypassing every other handler. Use it when you want an event to reach
logfire but not your local stderr/file sinks:

```python
logger = mollog.get_logger("api")

logger.info("served locally")                       # mollog + logfire
logger.fire("shipped to logfire only", status=200)  # logfire only
logger.fire("warning event", level="warning", code=42)
```

`logger.fire(...)` raises `RuntimeError` if no `LogfireHandler` is
reachable via the logger's chain (self + ancestors honoring `propagate`).

## Spans via `Context.scope`

`Context.scope(name, **attrs)` unifies mollog's scoped context with
logfire's span API. When `name` is provided **and** logfire is
configured, a matching `logfire.span(name, **attrs)` is opened for the
duration of the block:

```python
from mollog import Context, get_logger

logger = get_logger("api")

with Context.scope("request", user_id=42):
    logger.info("processed locally")       # mollog record, user_id=42
    logger.fire("processed", status=200)   # logfire event inside the span
```

If logfire is not configured (or not installed), `Context.scope` falls
back to a plain context-binding block so the same application code runs
in any environment.

## Merge order

A single event's attribute map is built as:

1. `Context.get()` (current `Context.bind` / `scope` fields)
2. `Logger.bind(...)` fields
3. keyword arguments passed to `logger.fire(...)` / `logger.info(...)`

Later sources win. `LogfireHandler` adds `logger_name` automatically if
the record has one.
