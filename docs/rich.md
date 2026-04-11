# Rich Console Logging

`mollog` keeps `rich` optional so the core package stays lightweight. If you want colored, more readable terminal logs for local tooling, install the extra:

```bash
pip install -e ".[rich]"
```

## Basic usage

```python
from mollog import Logger, RichHandler

logger = Logger("cli")
logger.add_handler(RichHandler())

logger.info("render complete", frame=128)
logger.warning("value outside expected range", field="charge", observed="2+")
```

## Configuration

`RichHandler` supports:

- custom `Console` injection
- level filtering
- optional timestamp rendering
- optional logger name rendering
- optional extra-field rendering
- optional `markup` support

Example:

```python
import io

from rich.console import Console

from mollog import Logger, RichHandler

buffer = io.StringIO()
console = Console(file=buffer, force_terminal=False, color_system=None)

logger = Logger("tests")
logger.add_handler(RichHandler(console=console, show_time=False))
logger.info("captured output", case="rich-handler")
```

## Formatter interaction

By default, `RichHandler` renders a structured line from the log record itself.

If you call `set_formatter(...)`, the handler respects that formatter and prints the formatted string through Rich instead:

```python
from mollog import JSONFormatter, Logger, RichHandler

logger = Logger("cli")
handler = RichHandler()
handler.set_formatter(JSONFormatter())
logger.add_handler(handler)
```

This is useful when you still want Rich's console integration but need exact formatter output.
