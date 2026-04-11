# mollog

Small, typed, dependency-free logging for Python applications that need structured output without hauling in a full observability stack.

[Get started](getting-started.md){ .md-button .md-button--primary }
[API reference](api.md){ .md-button }

## What it gives you

- Named loggers with propagation and hierarchy support
- Structured `extra` fields and reusable context via `bind()`
- Exception and stack capture on every record
- Context-local structured fields for async and request-scoped flows
- Text and JSON formatters
- Stream, file, rotating-file, timed-rotating, queue, and null handlers
- Optional Rich console output for local tooling and CLIs
- Queue listeners for thread and multiprocessing pipelines
- No runtime dependencies

## Design goals

### Minimal surface area

`mollog` stays close to the standard Python logging mental model, but removes a lot of ceremony:

- logger construction is explicit
- handlers are small and composable
- records are immutable dataclasses
- structured context is first-class instead of bolted on

### Predictable behavior

Recent hardening work focused on the edges that tend to turn into production bugs:

- logger and manager mutation are guarded for concurrent access
- formatter reserved keys cannot overwrite core record fields
- queue listener shutdown drains late-arriving records for a short grace window
- rotating handlers validate invalid values up front
- optional `RichHandler` integrates without forcing `rich` into core installs
- top-level `configure()` and `shutdown()` cover common app lifecycle setup

## Typical use cases

- CLI tools that need human-readable stderr output
- services that want newline-delimited JSON logs
- worker pools that centralize writes through a queue
- scientific or data-processing pipelines that carry rich contextual metadata

## Next steps

- Follow the [getting started guide](getting-started.md) for setup and examples.
- Read [configuration](configuration.md) for root logger setup and teardown.
- Read [context propagation](context.md) for request or task scoped metadata.
- Check [Rich console logging](rich.md) if you want colored terminal output.
- Read [behavior and guarantees](behavior.md) for important runtime semantics.
- Browse the [API reference](api.md) for the exported surface.
