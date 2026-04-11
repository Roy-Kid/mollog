# Context Propagation

`mollog` supports context-local structured fields using Python `contextvars`.

This is useful for:

- request IDs in async services
- trace IDs in worker pools
- tenant or batch IDs in data pipelines
- any field that should follow the current execution flow without being passed manually every time

## Bind fields globally for the current context

```python
from mollog import bind_context, get_logger, reset_context

logger = get_logger("api")
token = bind_context(request_id="req-7", trace_id="trace-9")

try:
    logger.info("accepted")
finally:
    reset_context(token)
```

## Use a scoped context

```python
from mollog import get_logger, scoped_context

logger = get_logger("worker")

with scoped_context(batch="nightly", request_id="req-42"):
    logger.info("started")
```

## Merge behavior

Field precedence is:

1. context-local fields
2. bound logger fields
3. per-call `extra`

Later sources overwrite earlier ones. That means explicit per-call values always win.
