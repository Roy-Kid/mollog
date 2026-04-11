"""mollog — zero-dependency structured logging for molcrafts."""

from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING

from mollog.context import bind_context, clear_context, get_context, reset_context, scoped_context
from mollog.file_handler import FileHandler, RotatingFileHandler, TimedRotatingFileHandler
from mollog.filter import Filter, LevelFilter
from mollog.formatter import Formatter, JSONFormatter, TextFormatter
from mollog.handler import Handler, NullHandler, StreamHandler
from mollog.level import Level
from mollog.logger import BoundLogger, Logger
from mollog.manager import LoggerManager, configure, get_logger, shutdown
from mollog.queue import QueueHandler, QueueListener
from mollog.record import LogRecord

if TYPE_CHECKING:
    from mollog.rich_handler import RichHandler

try:
    __version__ = version("mollog")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = [
    "__version__",
    "Level",
    "LogRecord",
    "Formatter",
    "TextFormatter",
    "JSONFormatter",
    "Filter",
    "LevelFilter",
    "Handler",
    "StreamHandler",
    "NullHandler",
    "FileHandler",
    "RotatingFileHandler",
    "TimedRotatingFileHandler",
    "QueueHandler",
    "QueueListener",
    "Logger",
    "BoundLogger",
    "LoggerManager",
    "configure",
    "get_logger",
    "shutdown",
    "bind_context",
    "clear_context",
    "get_context",
    "reset_context",
    "scoped_context",
    "RichHandler",
]


def __getattr__(name: str) -> object:
    if name == "RichHandler":
        from mollog.rich_handler import RichHandler

        return RichHandler
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
