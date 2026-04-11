# Contributing

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

If you want to work on the documentation site:

```bash
pip install -e ".[docs]"
```

## Local Checks

Run lint and tests before opening a pull request:

```bash
ruff check .
pytest -q
```

If documentation dependencies are installed, preview docs locally:

```bash
zensical serve
```

## Change Expectations

- Keep the runtime package dependency free.
- Add tests for behavior changes and bug fixes.
- Preserve backwards compatibility for public APIs unless the change is explicitly scheduled for a major release.
- Update `README.md`, `docs/`, and `CHANGELOG.md` when behavior or public interfaces change.

## Pull Requests

- Keep PRs scoped to one logical change.
- Describe user-visible impact clearly.
- Include migration notes when behavior changes.
