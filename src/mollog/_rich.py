from __future__ import annotations

import threading
from typing import Any, Literal

from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.text import Text

from mollog._formatter import Formatter
from mollog._level import Level
from mollog._record import LogRecord

ColorSystem = Literal["auto", "standard", "256", "truecolor", "windows"]


class RichFormatter(Formatter):
    """Formatter that produces ANSI-styled lines via ``rich``.

    Pair with any handler that writes strings (``StreamHandler``,
    ``FileHandler``, ...) — this formatter's only job is turning a
    :class:`LogRecord` into a colored, well-laid-out string.
    """

    _LEVEL_STYLES: dict[Level, str] = {
        Level.TRACE: "dim",
        Level.DEBUG: "cyan",
        Level.INFO: "green",
        Level.WARNING: "yellow",
        Level.ERROR: "bold red",
        Level.CRITICAL: "bold white on red",
    }

    def __init__(
        self,
        *,
        show_time: bool = True,
        show_logger_name: bool = True,
        show_extra: bool = True,
        markup: bool = False,
        highlighter: ReprHighlighter | None = None,
        time_format: str = "%H:%M:%S",
        color_system: ColorSystem | None = "truecolor",
        force_terminal: bool = True,
    ) -> None:
        self._show_time = show_time
        self._show_logger_name = show_logger_name
        self._show_extra = show_extra
        self._markup = markup
        self._time_format = time_format
        self._highlighter = highlighter or ReprHighlighter()
        self._console = Console(
            force_terminal=force_terminal,
            color_system=color_system,
            highlight=False,
            soft_wrap=True,
        )
        self._lock = threading.Lock()

    def format(self, record: LogRecord) -> str:
        with self._lock:
            parts: list[str] = [self._capture(self._render(record))]
            if record.exception:
                parts.append(self._capture(Text(record.exception, style="red")))
            if record.stack_info:
                header = Text("Stack (most recent call last):", style="magenta")
                body = Text(record.stack_info, style="magenta")
                parts.append(self._capture(header))
                parts.append(self._capture(body))
            return "\n".join(parts)

    def _capture(self, renderable: Any) -> str:
        with self._console.capture() as capture:
            self._console.print(renderable, markup=self._markup, end="")
        return capture.get()

    def _render(self, record: LogRecord) -> Text:
        segments: list[str | Text | tuple[str, str]] = []
        style = self._LEVEL_STYLES.get(record.level, "")

        if self._show_time:
            segments.extend([(record.timestamp.strftime(self._time_format), "dim"), " "])

        segments.extend([(f"{record.level!s:<8s}", style), " "])

        if self._show_logger_name:
            segments.extend([(record.logger_name or "root", "bold blue"), " "])

        message_style = "bold" if record.level >= Level.ERROR else ""
        segments.append((record.message, message_style))

        if self._show_extra and record.extra:
            segments.append(" ")
            segments.append(self._highlighter(repr(record.extra)))

        return Text.assemble(*segments)
