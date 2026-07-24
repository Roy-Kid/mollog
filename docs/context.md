# Context Propagation

`mollog` supports context-local structured fields using Python `contextvars`.

This is useful for:

- request IDs in async services
- trace IDs in worker pools
- tenant or batch IDs in data pipelines
- any field that should follow the current execution flow without being passed manually every time

All context operations live under the `Context` namespace class.

## Bind fields globally for the current context

```python
from mollog import Context, get_logger

logger = get_logger("api")
token = Context.bind(request_id="req-7", trace_id="trace-9")

try:
    logger.info("accepted")
finally:
    Context.reset(token)
```

## Use a scoped context

```python
from mollog import Context, get_logger

logger = get_logger("worker")

with Context.scope(batch="nightly", request_id="req-42"):
    logger.info("started")
```

## Named scopes and logfire spans

When you pass a `name` to `Context.scope(...)`, it records a `scope` field
in the context *and* opens a matching `logfire` span if
[logfire is configured](logfire.md):

```python
from mollog import Context, get_logger

logger = get_logger("api")

with Context.scope("request", user_id=42):
    logger.info("handling")         # mollog record carries scope="request"
    logger.fire("handled")          # logfire event attached to the span
```

`logger.fire(...)` only reaches logfire if a `LogfireHandler` is attached
to the logger chain (see [Logfire](logfire.md)); it raises `RuntimeError`
otherwise. If logfire isn't configured, the span is a no-op and the scope
still works as a plain bind/reset block.

## Merge behavior

Field precedence is:

1. context-local fields (`Context.bind` / `Context.scope`)
2. logger-bound fields (`Logger.bind`)
3. per-call `extra`

Later sources overwrite earlier ones. That means explicit per-call values always win.
