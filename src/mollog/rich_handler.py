from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mollog.handler import Handler
from mollog.level import Level
from mollog.record import LogRecord

if TYPE_CHECKING:
    from rich.console import Console
    from rich.highlighter import Highlighter
    from rich.text import Text


class RichHandler(Handler):
    """Pretty console handler backed by the optional ``rich`` package."""

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
        console: Console | None = None,
        level: Level = Level.TRACE,
        *,
        show_time: bool = True,
        show_logger_name: bool = True,
        show_extra: bool = True,
        markup: bool = False,
        highlighter: Highlighter | None = None,
        time_format: str = "%H:%M:%S",
    ) -> None:
        super().__init__(level)
        console_cls, repr_highlighter_cls, text_cls = _load_rich()

        self._console = console or console_cls(stderr=True)
        self._show_time = show_time
        self._show_logger_name = show_logger_name
        self._show_extra = show_extra
        self._markup = markup
        self._time_format = time_format
        self._formatter_overridden = False
        self._text_cls = text_cls
        self._highlighter = highlighter or repr_highlighter_cls()

    def set_formatter(self, formatter: Any) -> None:
        super().set_formatter(formatter)
        self._formatter_overridden = True

    def emit(self, record: LogRecord) -> None:
        style = self._LEVEL_STYLES.get(record.level, "")
        if self._formatter_overridden:
            line = self._formatter.format(record)
            self._console.print(line, style=style, markup=self._markup)
            return

        self._console.print(self._render_record(record), markup=self._markup)
        if record.exception:
            self._console.print(record.exception, style="red", markup=False)
        if record.stack_info:
            self._console.print("Stack (most recent call last):", style="magenta", markup=False)
            self._console.print(record.stack_info, style="magenta", markup=False)

    def _render_record(self, record: LogRecord) -> Text:
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

        return self._text_cls.assemble(*segments)


def _load_rich() -> tuple[type[Console], type[Highlighter], type[Text]]:
    try:
        from rich.console import Console
        from rich.highlighter import ReprHighlighter
        from rich.text import Text
    except ImportError as exc:
        raise ImportError(
            "RichHandler requires the optional 'rich' dependency. Install mollog[rich]."
        ) from exc

    return Console, ReprHighlighter, Text
