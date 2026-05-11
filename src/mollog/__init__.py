"""mollog — structured logging for molcrafts."""

import logging as _stdlib_logging
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
    basicConfig,
    configure,
    critical,
    debug,
    error,
    exception,
    get_logger,
    getLogger,
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

# Level constants: taken straight from stdlib `logging` so that
# `mollog.WARNING is logging.WARNING` (same plain `int`, no enum
# substitution). TRACE is mollog's superset addition — stdlib has no
# equivalent.
NOTSET = _stdlib_logging.NOTSET
DEBUG = _stdlib_logging.DEBUG
INFO = _stdlib_logging.INFO
WARNING = _stdlib_logging.WARNING
WARN = _stdlib_logging.WARN
ERROR = _stdlib_logging.ERROR
CRITICAL = _stdlib_logging.CRITICAL
FATAL = _stdlib_logging.FATAL
TRACE = int(Level.TRACE)


__all__ = [
    "__version__",
    "Context",
    "Level",
    "NOTSET",
    "TRACE",
    "DEBUG",
    "INFO",
    "WARNING",
    "WARN",
    "ERROR",
    "CRITICAL",
    "FATAL",
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
    "basicConfig",
    "configure",
    "configure_logfire",
    "getLogger",
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
