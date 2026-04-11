# Release Notes

## 1.0.0

`mollog` 1.0.0 is the first stable release.

### Included in this release

- thread-safe logger and manager operations
- optional `RichHandler` with lazy import behavior
- `exc_info`, `stack_info`, and `logger.exception(...)`
- context-local structured fields via `contextvars`
- `configure()` and `shutdown()` helpers
- stronger packaging metadata and release assets
- Zensical documentation site
- GitHub Actions for tests, docs, build validation, and release publishing

### Suggested release sequence

1. Ensure the CI workflow is green.
2. Build artifacts locally or from CI.
3. Tag the release as `v1.0.0`.
4. Publish a GitHub release.
5. Let the publish workflow upload the distribution to PyPI once trusted publishing is configured.
