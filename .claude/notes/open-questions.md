# Open questions

Things bootstrap was uncertain about. Resolve them as the project
clarifies; remove an entry once decided and (if generally applicable)
promote the answer to `CLAUDE.md` or `notes.md`.

## Open

- **Docstring style migration.** `mol_project.doc.style` is set to
  `google` as the **target**, but the existing public-API docstrings
  (e.g. `Logger.set_level`, `LoggerManager.configure`,
  `Logger.fire`, `Logger.bind`) use **Sphinx-native** style: PEP 257
  imperative summary + free prose with `:class:` / `:func:` /
  `:mod:` cross-references and no `Args:` / `Returns:` / `Raises:`
  sections. Migrate the public surface to Google-style incrementally
  on next `/mol:docs` pass — do not rewrite all at once. Internal
  helpers (`_log`, `_dispatch`, `_resolve_exc_info`) can stay
  Sphinx-native.

## Resolved during bootstrap

(Kept here briefly for traceability; remove once the decisions feel
boring.)

- **Reserved-attribute drift between `_formatter.py` and
  `_stdlib_bridge.py`.** Resolved: not drift. `_RESERVED_FIELDS`
  blocks user `extra=` keys from clobbering mollog's own `LogRecord`
  slots; `_RESERVED_STDLIB_ATTRS` is the *exclusion set* for pulling
  user-set extras off a stdlib `LogRecord`. Two record models, two
  reserved sets, intentionally distinct. Captured in `notes.md`.
- **`exception()` signature asymmetry.** Resolved: intentional,
  mirrors `logging.exception` — `exc_info=True` is hardcoded on
  purpose, exposing it as a kwarg would defeat the convenience.
  Captured in `notes.md`.
