"""mollog — structured logging for molcrafts."""

from importlib.metadata import PackageNotFoundError, version

from mollog._context import Context
from mollog._file_handler import FileHandler, RotatingFileHandler, TimedRotatingFileHandler
from mollog._filter import Filter, LevelFilter
from mollog._formatter import Formatter, JSONFormatter, TextFormatter
from mollog._handler import Handler, NullHandler, StreamHandler
from mollog._level import Level
from mollog._logfire import LogfireHandler, configure_logfire
from mollog._logger import Logger
from mollog._manager import LoggerManager, configure, get_logger, shutdown
from mollog._queue import QueueHandler, QueueListener
from mollog._record import LogRecord
from mollog._rich import RichFormatter

try:
    __version__ = version("mollog")
except PackageNotFoundError:
    __version__ = "0+unknown"


__all__ = [
    "__version__",
    "Context",
    "Level",
    "LogRecord",
    "Formatter",
    "TextFormatter",
    "JSONFormatter",
    "RichFormatter",
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
    "LogfireHandler",
    "Logger",
    "LoggerManager",
    "configure",
    "configure_logfire",
    "get_logger",
    "shutdown",
]
