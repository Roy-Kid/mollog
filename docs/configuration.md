# Configuration

`mollog.configure()` is the single entry point for application-wide setup. It mirrors `logging.basicConfig` so projects can migrate without re-learning the surface, and adds optional capture of stdlib `logging` records.

## Replace `logging.basicConfig`

```python
import mollog

mollog.configure(
    level="INFO",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
mollog.get_logger("httpx").set_level("WARNING")

mollog.info("service booted", port=8080)
```

`format=` accepts the standard `%(asctime)s %(levelname)s %(name)s %(message)s` placeholders (rendered through `StdlibStyleFormatter`). Pair with `datefmt=` to control the `asctime` strftime pattern.

`format=` and `formatter=` are mutually exclusive — pass a `format` string for stdlib-style templates, or a `Formatter` instance for full control.

## Capture stdlib `logging` records

By default, `mollog.configure(...)` installs a `StdlibBridgeHandler` on stdlib's root logger so that third-party libraries which emit through `logging` (httpx, urllib3, openai, …) flow through mollog. Per-logger levels set via `Logger.set_level()` apply uniformly — and propagate to stdlib so the record is dropped at the source.

```python
mollog.get_logger("httpx").set_level("WARNING")  # silences httpx's INFO chatter
```

Disable the bridge if you want to leave stdlib alone:

```python
mollog.configure(level="INFO", capture_stdlib=False)
```

You can also manage the bridge directly:

```python
from mollog import capture_stdlib_logging, release_stdlib_logging

capture_stdlib_logging()       # install
release_stdlib_logging()       # remove
```

## Default stream setup

If you do not pass handlers, `configure()` installs a default `StreamHandler` to `stderr`:

```python
mollog.configure(level="WARNING")
```

## Mirror to a file

```python
mollog.configure(
    level="INFO",
    filename="app.log",
    file_level="DEBUG",  # file gets DEBUG, terminal stays at INFO
)
```

## Replacing vs extending handlers

By default, `configure()` replaces existing root handlers and closes them.

```python
mollog.configure(level="INFO", replace=True)
```

If you want to preserve current root handlers and add more:

```python
mollog.configure(level="DEBUG", handlers=[my_handler], replace=False)
```

## Top-level shortcuts

After `configure()`, the root logger is reachable through module-level helpers, mirroring stdlib:

```python
mollog.info("started")
mollog.warning("disk almost full", free_gb=2)
mollog.set_level("DEBUG")
```

Level constants are also exposed: `mollog.TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

## Shutdown

Use `shutdown()` during application teardown to close handlers, remove any installed stdlib bridge, and clear context-local state:

```python
mollog.shutdown()
```

`mollog` also registers `shutdown()` as an `atexit` hook on import, so file handles do not leak on normal interpreter exit.
