# Operations

## Start and stop

1. Copy `.env.example` to `.env`. Set `MESH_COMPUTE_ADMIN_TOKEN` to a long random secret and keep `.env` out of version control.
2. Run `docker compose up --build`. Compose waits for PostgreSQL health, applies Alembic migrations, and starts the coordinator and two workers.
3. Use the API docs at `http://localhost:8000/docs`; the project site is deployed separately at `https://nihalmachhi.github.io/MeshCompute/`.
4. Stop with `docker compose down`. Removing the named database volume deletes persisted jobs and results.

## Authentication

Use `Authorization: Bearer <MESH_COMPUTE_ADMIN_TOKEN>` for job submission, job cancellation, worker registration, and worker inventory. Registration returns a per-worker token. The coordinator stores only its SHA-256 digest; workers send the issued token for claim, heartbeat, start, completion, and failure operations. Missing admin configuration fails closed. Do not expose the admin token in logs or public clients.

## Limits and retention

- `MESH_COMPUTE_MAX_RESULT_BYTES` caps serialized task output (default 10,000,000 bytes). Oversized output returns HTTP 413 without committing task completion.
- `MESH_COMPUTE_RESULT_RETENTION_SECONDS` sets terminal job/result retention (default 604,800 seconds). A background purger deletes expired terminal job data and dependent rows.
- `MESH_COMPUTE_WORKER_STALE_SECONDS` marks silent workers stale; `MESH_COMPUTE_WORKER_OFFLINE_SECONDS` moves long-stale workers offline; `MESH_COMPUTE_WORKER_RETENTION_SECONDS` removes old offline records when they no longer own a task.
- `MESH_COMPUTE_LEASE_TTL_SECONDS` controls the worker lease. A task can finish after its timestamp expires while it still owns the same attempt; once reaped and reassigned, the incremented attempt fences the old worker.

## Failure behavior

Attempts are at least once. A worker may repeat a handler after a lease expires, so external side effects must be idempotent. Results use attempt fencing and a unique task-result key. Outbox events are committed with state changes and delivered at least once; a crash after a live notification but before marking the outbox row can cause a duplicate. WebSocket subscribers are process-local, so run one coordinator instance for this demo.

## Task dependency graphs

`POST /api/v1/jobs` accepts optional `task_dependencies` pairs of task indices. Indices refer to the deterministic chunks returned by the selected handler's planner. Use the same `input_ref` and `options` you submit to estimate chunking; malformed indices, duplicate edges, and cycles are rejected. A dependent task becomes claimable only after every prerequisite completes. A terminal prerequisite failure cancels queued descendants. This is ordering only: task outputs are not injected into downstream task inputs. `GET /api/v1/jobs/{job_id}/dag` reports edges and a unit-cost critical path, not a runtime forecast.

## Queue priority and worker capabilities

`POST /api/v1/jobs` may set integer `priority` from 0 through 10 and a list of
`required_capabilities`. Worker registration includes a declared capability list; the
claim query only assigns tasks whose requirements are a subset of that declaration. The
default worker advertises `python`. These are operator-provided labels, not hardware
attestation. The coordinator adds one priority level per `MESH_COMPUTE_PRIORITY_AGING_SECONDS`
of queue wait, with a default interval of 30 seconds; jobs at the same effective priority
continue to use per-job fairness.

## Verification

Run `uv run pytest -q --cov=meshcompute --cov-fail-under=80`, `uv run alembic upgrade head && uv run alembic check`, and `docker compose config -q`. The PostgreSQL integration tests require a reachable PostgreSQL database configured by `MESH_COMPUTE_DATABASE_URL`.
