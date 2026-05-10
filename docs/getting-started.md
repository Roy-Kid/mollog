# Getting Started

## Install

```bash
pip install molcrafts-mollog
```

For development with tests and docs tooling:

```bash
pip install -e ".[dev,docs]"
```

To opt into the [Pydantic Logfire](https://logfire.pydantic.dev) backend:

```bash
pip install "molcrafts-mollog[logfire]"
```

## Migrate from `logging`

`mollog` is a drop-in for `logging.basicConfig`. The three lines you would normally write against stdlib become three lines of mollog:

```python
import mollog

mollog.configure(
    level="INFO",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
mollog.get_logger("httpx").set_level("WARNING")

mollog.info("service booted", port=8080)
```

That is the whole story:

- `configure(format=...)` accepts stdlib `%(asctime)s`-style format strings.
- `get_logger(name).set_level(...)` accepts level names, ints, or `Level` members; the call also propagates to `logging.getLogger(name)` so libraries that still emit through stdlib are silenced at the source.
- The default `capture_stdlib=True` routes any third-party `logging` record (httpx, urllib3, openai, …) through mollog so a single configuration governs the whole process.

## Configure with explicit handlers

```python
from mollog import JSONFormatter, StreamHandler, configure, get_logger

handler = StreamHandler()
handler.set_formatter(JSONFormatter())
configure(level="info", handlers=[handler])

logger = get_logger("api")
logger.info("request completed", status=200, duration_ms=18)
```

## Bind reusable context

```python
from mollog import get_logger

logger = get_logger("pipeline")
run_logger = logger.bind(run_id="r-2026-04-11", batch="alpha")
run_logger.info("batch started")
run_logger.warning("low confidence", score=0.63)
```

## Build a hierarchy

```python
from mollog import LoggerManager

manager = LoggerManager()
root = manager.root
app = manager.get_logger("app")
db = manager.get_logger("app.db")
```

Child loggers dispatch to their own handlers first and then propagate upward when `propagate=True`.

## Add context-local fields

```python
from mollog import Context, get_logger

logger = get_logger("api")

with Context.scope("accept-request", request_id="req-42", trace_id="trace-7"):
    logger.info("accepted")
```

## Use a queue listener

```python
import queue

from mollog import Logger, QueueHandler, QueueListener, StreamHandler

q: queue.Queue[object] = queue.Queue()
logger = Logger("worker")
logger.add_handler(QueueHandler(q))

with QueueListener(q, StreamHandler()):
    logger.info("task accepted", task_id="t-1")
```

## Add Rich console output

```python
from mollog import Logger, RichFormatter, StreamHandler

handler = StreamHandler()
handler.set_formatter(RichFormatter())
logger = Logger("cli")
logger.add_handler(handler)
logger.info("rendering preview", width=120, height=80)
```

## Log exceptions

`mollog` can capture formatted exception traces and stack information directly on the record:

```python
import mollog

try:
    raise ValueError("bad payload")
except ValueError:
    mollog.exception("request failed", request_id="req-17")
```

You can also attach stack information without an active exception:

```python
mollog.warning("unexpected branch", stack_info=True, node="fallback")
```

## Serve the documentation locally

```bash
zensical serve
```

Build the static site:

```bash
zensical build
```
