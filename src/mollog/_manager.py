from __future__ import annotations

import sys
import threading
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import IO, Any

from mollog._context import Context
from mollog._file_handler import FileHandler
from mollog._formatter import Formatter, StdlibStyleFormatter, TextFormatter
from mollog._handler import Handler, StreamHandler
from mollog._level import Level
from mollog._logger import ExcInfoArg, Logger
from mollog._stdlib_bridge import capture_stdlib_logging, release_stdlib_logging


class LoggerManager:
    """Singleton registry of loggers with hierarchy support."""

    _instance: LoggerManager | None = None
    _init_lock = threading.Lock()

    _loggers: dict[str, Logger]
    _root: Logger
    _configured: bool
    _state_lock: threading.RLock

    def __new__(cls) -> LoggerManager:
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._loggers = {}
                    inst._root = Logger("", Level.INFO)
                    inst._loggers[""] = inst._root
                    inst._configured = False
                    inst._state_lock = threading.RLock()
                    cls._instance = inst
        return cls._instance

    @property
    def root(self) -> Logger:
        return self._root

    def get_logger(self, name: str = "") -> Logger:
        with self._state_lock:
            if name in self._loggers:
                return self._loggers[name]

            logger = Logger(name)
            self._loggers[name] = logger

            parts = name.rsplit(".", 1)
            if len(parts) > 1:
                parent_name = parts[0]
                logger.parent = self.get_logger(parent_name)
            else:
                logger.parent = self._root

            return logger

    def ensure_default_handler(self) -> None:
        """Add a default StreamHandler to root if it has none.

        Hot path — every ``mollog.info(...)``-style call goes through here
        via ``get_logger("")``. The fast path avoids the lock once the
        manager has been configured.
        """
        if self._configured:
            return
        with self._state_lock:
            if not self._configured and not self._root.handlers:
                handler = StreamHandler(stream=sys.stderr, level=Level.INFO)
                handler.set_formatter(TextFormatter())
                self._root.add_handler(handler)
                self._configured = True

    def configure(
        self,
        *,
        level: Level | str | int = Level.INFO,
        handlers: Iterable[Handler] | None = None,
        formatter: Formatter | None = None,
        format: str | None = None,
        datefmt: str | None = None,
        replace: bool = True,
        stream: IO[str] | None = None,
        filename: str | Path | None = None,
        filemode: str = "a",
        file_level: Level | str | int | None = None,
        file_formatter: Formatter | None = None,
        encoding: str = "utf-8",
        capture_stdlib: bool = True,
    ) -> Logger:
        """Configure the root logger for library or application use.

        Parameters mirror :func:`logging.basicConfig` where sensible. The
        important dual-destination case — ``stream + filename`` — attaches
        *both* a :class:`StreamHandler` and a :class:`FileHandler` to the
        root logger so records show up on the terminal **and** in the file.

        Precedence rules:

        * If *handlers* is given, it fully overrides *stream* / *filename*:
          the caller is taking manual control of the handler list. A
          shared *formatter* (if given) is still applied to each handler.
        * Otherwise a :class:`StreamHandler` is always added (on *stream*
          or ``sys.stderr``). If *filename* is also provided, a
          :class:`FileHandler` is added alongside it.
        * *file_level* / *file_formatter* let the file sink diverge from
          the console (e.g. DEBUG to file, INFO to terminal).
        * *format* accepts a stdlib :func:`logging.basicConfig`-style
          format string (``"%(asctime)s %(levelname)s %(name)s %(message)s"``)
          and is rendered through :class:`StdlibStyleFormatter`. Mutually
          exclusive with *formatter* — pass one or the other.
        * *capture_stdlib* (default ``True``) installs a
          :class:`StdlibBridgeHandler` on stdlib's root logger so that
          third-party libraries which emit through :mod:`logging`
          (httpx, urllib3, …) flow through mollog's hierarchy. Pass
          ``False`` to leave stdlib alone.
        """

        if formatter is not None and format is not None:
            raise ValueError("pass either `formatter` or `format`, not both")

        resolved_level = Level.coerce(level)
        resolved_file_level = Level.coerce(file_level) if file_level is not None else resolved_level

        if formatter is None and format is not None:
            formatter = StdlibStyleFormatter(format, datefmt=datefmt)

        with self._state_lock:
            root = self._root
            root.level = resolved_level

            if replace:
                root.clear_handlers(close=True)

            provided = list(handlers or [])
            if provided:
                if formatter is not None:
                    for handler in provided:
                        handler.set_formatter(formatter)
                for handler in provided:
                    root.add_handler(handler)
            elif replace or not root.handlers:
                shared_formatter = formatter or TextFormatter()

                stream_handler = StreamHandler(
                    stream=stream or sys.stderr,
                    level=resolved_level,
                )
                stream_handler.set_formatter(shared_formatter)
                root.add_handler(stream_handler)

                if filename is not None:
                    file_handler = FileHandler(
                        Path(filename),
                        mode=filemode,
                        encoding=encoding,
                        level=resolved_file_level,
                    )
                    file_handler.set_formatter(file_formatter or shared_formatter)
                    root.add_handler(file_handler)

            self._configured = True

        if capture_stdlib:
            capture_stdlib_logging(replace=replace)
        elif replace:
            release_stdlib_logging()

        return root

    def shutdown(self) -> None:
        """Close all registered handlers and clear runtime state.

        Also removes any :class:`StdlibBridgeHandler` installed on
        stdlib's root logger.
        """

        with self._state_lock:
            closed: set[int] = set()
            for logger in self._loggers.values():
                handlers = tuple(logger.handlers)
                logger.clear_handlers(close=False)
                for handler in handlers:
                    ident = id(handler)
                    if ident in closed:
                        continue
                    handler.close()
                    closed.add(ident)
            self._configured = False
        release_stdlib_logging()
        Context.clear()

    def _reset(self) -> None:
        """Reset state (for testing only)."""
        with self._state_lock:
            self._loggers.clear()
            self._root = Logger("", Level.INFO)
            self._loggers[""] = self._root
            self._configured = False
        release_stdlib_logging()


def get_logger(name: str = "") -> Logger:
    """Get or create a logger by name.

    On first call, attaches a default StreamHandler to the root logger
    if no handlers are configured.
    """
    mgr = LoggerManager()
    mgr.ensure_default_handler()
    return mgr.get_logger(name)


def getLogger(name: str | None = None) -> Logger:
    """Drop-in alias for :func:`logging.getLogger`.

    Accepts ``None`` (the stdlib convention for "give me the root
    logger") as well as the empty string. Otherwise identical to
    :func:`get_logger`.
    """

    return get_logger(name or "")


def configure(
    *,
    level: Level | str | int = Level.INFO,
    handlers: Iterable[Handler] | None = None,
    formatter: Formatter | None = None,
    format: str | None = None,
    datefmt: str | None = None,
    replace: bool = True,
    stream: IO[str] | None = None,
    filename: str | Path | None = None,
    filemode: str = "a",
    file_level: Level | str | int | None = None,
    file_formatter: Formatter | None = None,
    encoding: str = "utf-8",
    capture_stdlib: bool = True,
) -> Logger:
    """Configure and return the root logger.

    See :meth:`LoggerManager.configure` for the full parameter reference.
    Pass *format* (stdlib ``%(asctime)s`` style) instead of *formatter*
    if you're migrating from :func:`logging.basicConfig`.
    *capture_stdlib* (default ``True``) routes stdlib :mod:`logging`
    records through mollog so libraries like httpx are governed by the
    same hierarchy.
    """

    return LoggerManager().configure(
        level=level,
        handlers=handlers,
        formatter=formatter,
        format=format,
        datefmt=datefmt,
        replace=replace,
        stream=stream,
        filename=filename,
        filemode=filemode,
        file_level=file_level,
        file_formatter=file_formatter,
        encoding=encoding,
        capture_stdlib=capture_stdlib,
    )


_BASIC_CONFIG_KEYS = frozenset(
    {
        "filename",
        "filemode",
        "format",
        "datefmt",
        "style",
        "level",
        "stream",
        "handlers",
        "force",
        "encoding",
        "errors",
    }
)


def basicConfig(**kwargs: Any) -> None:
    """Drop-in for :func:`logging.basicConfig`.

    Accepts the same kwargs as stdlib (*filename*, *filemode*, *format*,
    *datefmt*, *style*, *level*, *stream*, *handlers*, *force*,
    *encoding*, *errors*) with stdlib semantics:

    * No-op when the root logger already has handlers, unless
      ``force=True`` is passed (in which case existing handlers are
      removed first).
    * ``stream``, ``filename``, and ``handlers`` are mutually exclusive.
    * Returns ``None``.

    Under the hood this routes through :func:`configure`, so the stdlib
    :mod:`logging` bridge is installed and records emitted by
    third-party libraries flow through mollog's hierarchy. Use
    :func:`configure` directly if you need mollog-only features like
    simultaneous stream + file destinations.
    """

    unknown = set(kwargs) - _BASIC_CONFIG_KEYS
    if unknown:
        raise ValueError(f"Unrecognised argument(s): {', '.join(sorted(unknown))}")

    stream = kwargs.get("stream")
    filename = kwargs.get("filename")
    handlers = kwargs.get("handlers")
    if sum(x is not None for x in (stream, filename, handlers)) > 1:
        raise ValueError("'stream', 'filename', and 'handlers' are mutually exclusive")

    style = kwargs.get("style", "%")
    if style != "%":
        raise ValueError(
            f"basicConfig(style={style!r}) is not supported; mollog only "
            "renders '%' style format strings (see StdlibStyleFormatter)"
        )

    mgr = LoggerManager()
    if mgr.root.handlers and not kwargs.get("force", False):
        return

    level = kwargs.get("level")
    if level is None:
        level = mgr.root.level

    encoding = kwargs.get("encoding")

    mgr.configure(
        level=level,
        handlers=handlers,
        format=kwargs.get("format"),
        datefmt=kwargs.get("datefmt"),
        replace=True,
        stream=stream,
        filename=filename,
        filemode=kwargs.get("filemode", "a"),
        encoding=encoding if encoding is not None else "utf-8",
        capture_stdlib=True,
    )


def shutdown() -> None:
    """Close all configured handlers and clear context-local state."""

    LoggerManager().shutdown()


def set_level(level: Level | str | int) -> None:
    """Set the root logger's minimum level (mollog and stdlib bridge)."""

    get_logger("").set_level(level)


def _root_proxy(level_name: str) -> Callable[..., None]:
    """Build a module-level helper that forwards to ``get_logger("").<level_name>``.

    Stdlib-flavored helpers (``mollog.info(...)`` etc.) all share the same
    body — generate them from a single template instead of hand-writing
    six near-identical wrappers.
    """

    def _impl(
        message: str,
        *,
        exc_info: ExcInfoArg = None,
        stack_info: bool = False,
        **extra: Any,
    ) -> None:
        getattr(get_logger(""), level_name)(
            message, exc_info=exc_info, stack_info=stack_info, **extra
        )

    _impl.__name__ = level_name
    _impl.__qualname__ = level_name
    _impl.__doc__ = f"Log *message* at {level_name.upper()} on the root logger."
    return _impl


trace = _root_proxy("trace")
debug = _root_proxy("debug")
info = _root_proxy("info")
warning = _root_proxy("warning")
error = _root_proxy("error")
critical = _root_proxy("critical")


def exception(message: str, **extra: Any) -> None:
    get_logger("").exception(message, **extra)
