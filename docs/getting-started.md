# Getting Started

## Install

```bash
pip install -e .
```

For development with tests and docs tooling:

```bash
pip install -e ".[dev,docs,rich]"
```

## Configure the root logger

```python
from mollog import StreamHandler, TextFormatter, configure, get_logger

handler = StreamHandler()
handler.set_formatter(TextFormatter())
configure(level="info", handlers=[handler])

logger = get_logger("app")
logger.info("service booted", port=8080)
```

## Switch to JSON output

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
from mollog import Logger

logger = Logger("pipeline")
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
from mollog import get_logger, scoped_context

logger = get_logger("api")

with scoped_context(request_id="req-42", trace_id="trace-7"):
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

Install the optional extra:

```bash
pip install -e ".[rich]"
```

Then switch the console handler:

```python
from mollog import Logger, RichHandler

logger = Logger("cli")
logger.add_handler(RichHandler())
logger.info("rendering preview", width=120, height=80)
```

## Log exceptions

`mollog` can capture formatted exception traces and stack information directly on the record:

```python
from mollog import JSONFormatter, Logger, StreamHandler

logger = Logger("api")
handler = StreamHandler()
handler.set_formatter(JSONFormatter())
logger.add_handler(handler)

try:
    raise ValueError("bad payload")
except ValueError:
    logger.exception("request failed", request_id="req-17")
```

You can also attach stack information without an active exception:

```python
logger.warning("unexpected branch", stack_info=True, node="fallback")
```

## Serve the documentation locally

```bash
zensical serve
```

Build the static site:

```bash
zensical build
```
