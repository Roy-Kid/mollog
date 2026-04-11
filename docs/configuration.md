# Configuration

`mollog` 1.0.0 adds a top-level `configure()` helper for the common case where an application wants to configure the root logger once and then call `get_logger(...)` everywhere else.

## Basic setup

```python
from mollog import JSONFormatter, StreamHandler, configure

handler = StreamHandler()
handler.set_formatter(JSONFormatter())

configure(level="info", handlers=[handler])
```

## Default stream setup

If you do not pass handlers, `configure()` installs a default `StreamHandler` to `stderr`:

```python
from mollog import configure

configure(level="warning")
```

## Replacing vs extending handlers

By default, `configure()` replaces existing root handlers and closes them.

```python
configure(level="info", replace=True)
```

If you want to preserve current root handlers and add more:

```python
configure(level="debug", handlers=[my_handler], replace=False)
```

## Shutdown

Use `shutdown()` during application teardown to close handlers and clear context-local state:

```python
from mollog import shutdown

shutdown()
```

This is especially useful in test suites, short-lived CLIs, and worker processes.
