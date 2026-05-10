"""mollog — structured logging for molcrafts."""

from importlib.metadata import PackageNotFoundError, version

from mollog._context import Context
from mollog._file_handler import FileHandler, RotatingFileHandler, TimedRotatingFileHandler
from mollog._filter import Filter, LevelFilter
from mollog._formatter import Formatter, JSONFormatter, StdlibStyleFormatter, TextFormatter
from mollog._handler import Handler, NullHandler, StreamHandler
from mollog._level import Level
from mollog._logfire import LogfireHandler, configure_logfire
from mollog._logger import Logger
from mollog._manager import (
    LoggerManager,
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
from mollog._queue import QueueHandler, QueueListener
from mollog._record import LogRecord
from mollog._rich import RichFormatter
from mollog._stdlib_bridge import (
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
    "Context",
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
    "RichFormatter",
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
    "LogfireHandler",
    "StdlibBridgeHandler",
    "Logger",
    "LoggerManager",
    "configure",
    "configure_logfire",
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
    "capture_stdlib_logging",
    "release_stdlib_logging",
]
