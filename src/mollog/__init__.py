"""mollog — structured logging for molcrafts."""

from importlib.metadata import PackageNotFoundError, version

from mollog.context import bind_context, clear_context, get_context, reset_context, scoped_context
from mollog.file_handler import FileHandler, RotatingFileHandler, TimedRotatingFileHandler
from mollog.filter import Filter, LevelFilter
from mollog.formatter import Formatter, JSONFormatter, StdlibStyleFormatter, TextFormatter
from mollog.handler import Handler, NullHandler, StreamHandler
from mollog.level import Level
from mollog.logger import BoundLogger, Logger
from mollog.manager import (
    LoggerManager,
    close_logger,
    configure,
    critical,
    debug,
    error,
    exception,
    get_logger,
    info,
    set_level,
    shutdown,
    trace,
    warning,
)
from mollog.queue import QueueHandler, QueueListener
from mollog.record import LogRecord
from mollog.rich_handler import RichHandler
from mollog.stdlib_bridge import (
    StdlibBridgeHandler,
    capture_stdlib_logging,
    release_stdlib_logging,
)

try:
    __version__ = version("mollog")
except PackageNotFoundError:
    __version__ = "0+unknown"

# Stdlib-compatible level constants for users migrating from `logging`.
TRACE = Level.TRACE
DEBUG = Level.DEBUG
INFO = Level.INFO
WARNING = Level.WARNING
ERROR = Level.ERROR
CRITICAL = Level.CRITICAL

__all__ = [
    "__version__",
    "Level",
    "TRACE",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "LogRecord",
    "Formatter",
    "TextFormatter",
    "JSONFormatter",
    "StdlibStyleFormatter",
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
    "close_logger",
    "configure",
    "get_logger",
    "set_level",
    "shutdown",
    "trace",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
    "bind_context",
    "clear_context",
    "get_context",
    "reset_context",
    "scoped_context",
    "RichHandler",
    "StdlibBridgeHandler",
    "capture_stdlib_logging",
    "release_stdlib_logging",
]
