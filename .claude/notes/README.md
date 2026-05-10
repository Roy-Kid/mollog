# `.claude/notes/` — passive internal context

This directory is the persistent, agent-readable side of the harness.
It holds knowledge that **outlives any single feature**:

- `notes.md` — evolving project decisions, captured by `/mol:note`.
- `architecture.md` — structured blueprint of modules, public surface,
  and layer roles. Populated and refreshed by `/mol:map`. Consumed by
  the `librarian` agent during `/mol:spec` Step 4.5.
- `open-questions.md` — things bootstrap was uncertain about; you fill
  these in over time.

Subdirectories may be added on demand when there is real content for
them: `contracts/`, `rubrics/`, `decisions/`, `debt/`, `handoffs/`.

## What does NOT live here

- Public-user documentation → `docs/`.
- Active runtime specs → `.claude/specs/` (alive while a feature is in
  flight, deleted on completion).
- Claude Code runtime config (skills, agents, hooks, settings) →
  `.claude/agents/`, `.claude/skills/`, `.claude/hooks/`,
  `.claude/settings*.json`.
