# Project notes

Evolving decisions and captured invariants. Append new entries with
`/mol:note`; promote a stable rule to `CLAUDE.md` once it has
stabilized.

## 2026-05-10 — Reserved-attribute sets are not redundant

`_RESERVED_FIELDS` in `src/mollog/_formatter.py` and
`_RESERVED_STDLIB_ATTRS` in `src/mollog/_stdlib_bridge.py` look like
parallel constants but serve opposite purposes:

- `_RESERVED_FIELDS` (mollog side) — set of mollog `LogRecord` slot
  names. Used by `_normalize_extra_fields` to **block** users from
  setting `extra={"timestamp": ...}` (or any other reserved name)
  via `logger.info(...)`, which would otherwise quietly clobber the
  record's own field at format time.
- `_RESERVED_STDLIB_ATTRS` (stdlib side) — set of stdlib
  `logging.LogRecord` built-in attribute names. Used by
  `_stdlib_record_extras` as the **exclusion set** when harvesting
  user-set fields off a stdlib record (anything *not* in the set is
  treated as a user extra and forwarded into mollog).

They are inverse uses of the same idea — a reserved-name allowlist on
one side, an exclusion list on the other — and live in their
respective record-model modules deliberately. Do not consolidate.

## 2026-05-10 — `exception()` deliberately omits `exc_info=`

`Logger.exception(message, **extra)` and the module-level
`mollog.exception(message, **extra)` hardcode `exc_info=True` and
intentionally do *not* expose `exc_info` as a keyword argument. This
mirrors `logging.exception` from the stdlib — the entire purpose of
`exception()` is to capture the active exception context
automatically; allowing the caller to pass `exc_info` would make it a
redundant alias for `error(..., exc_info=...)`. Asymmetry vs the
other six severity helpers is by design.
