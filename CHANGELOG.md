# Changelog

## [0.2.0] - 2026-11-02

### Fixed
- Worker child-process result collection now drains large results before joining; the multi-megabyte regression is covered.
- Job submissions reject unknown configuration keys by test, and `.env.example` values map to declared settings.
- Admin and worker APIs fail closed without the configured admin credential; workers use individually issued tokens stored as hashes.
- Service state notifications are written to an explicit PostgreSQL outbox in the same transaction as their state changes.
- The lease reaper runs synchronous database work in a worker thread instead of nesting an event loop.
- CSV aggregation uses record-aware byte ranges so each task reads only its chunk, including records with quoted newlines.
- Late results remain acceptable until a task is actually reassigned; attempt fencing rejects stale completions.
- Oversized task results are rejected, job cancellation fences active attempts, and terminal job data has a tested retention purge.
- Stale worker records transition offline and are purged after their configured retention period.

### Added
- Frozen initial schema and explicit transactional-outbox migration.
- CI gates for Ruff, mypy, coverage, PostgreSQL migrations, Compose validation, and the site.
- Regression and PostgreSQL integration tests for the documented behaviors.
- A MeshCompute cluster simulator site using Python-generated fixtures.
- Dependency-aware task DAG submission, topological release, critical-path estimate, and failure descendant cancellation.
- Generated synthetic vision and text duplicate-detection precision/recall in the site results.
- Readiness endpoint checks PostgreSQL independently from liveness.
- Pillow handlers enforce image format and pixel-count bounds for JPEG, PNG, and BMP inputs.

### Decisions
- Delivery from the database outbox to process-local WebSocket subscribers is at least once; duplicate notifications are possible after a crash.
- The service remains at-least-once and does not claim exactly-once side effects.
