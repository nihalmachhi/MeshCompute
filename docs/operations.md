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
- `MESH_COMPUTE_TASK_CPU_SECONDS`, `MESH_COMPUTE_TASK_MEMORY_BYTES`, and `MESH_COMPUTE_TASK_FILE_BYTES` apply POSIX limits to each handler child process (defaults: 300 CPU seconds, 1 GiB address space, and 10,000,000 bytes written). `MESH_COMPUTE_TASK_TIMEOUT_SECONDS` remains the wall-clock limit. These OS limits are applied in the Linux containers used by Compose; native Windows worker processes do not provide equivalent enforcement.
- `MESH_COMPUTE_RESULT_RETENTION_SECONDS` sets terminal job/result retention (default 604,800 seconds). A background purger deletes expired terminal job data and dependent rows.
- `MESH_COMPUTE_WORKER_STALE_SECONDS` marks silent workers stale; `MESH_COMPUTE_WORKER_OFFLINE_SECONDS` moves long-stale workers offline; `MESH_COMPUTE_WORKER_RETENTION_SECONDS` removes old offline records when they no longer own a task.
- `MESH_COMPUTE_LEASE_TTL_SECONDS` controls the worker lease. A task can finish after its timestamp expires while it still owns the same attempt; once reaped and reassigned, the incremented attempt fences the old worker.
- `MESH_COMPUTE_RETRY_BASE_SECONDS`, `MESH_COMPUTE_RETRY_MAX_SECONDS`, and `MESH_COMPUTE_RETRY_JITTER_FRACTION` control deterministic exponential retry delays. Retries remain pending but are not claimable until `available_at`.

## Failure behavior

Attempts are at least once. A worker may repeat a handler after a lease expires, so external side effects must be idempotent. Results use attempt fencing and a unique task-result key. Outbox rows and PostgreSQL `NOTIFY` wakeups are committed atomically with state changes. Each coordinator replica has its own durable-read cursor and local WebSocket fanout; notifications only wake readers, while polling after the cursor recovers missed wakeups and reconnects. WebSocket subscribers remain local to the coordinator handling their connection.

## Task dependency graphs

`POST /api/v1/jobs` accepts optional `task_dependencies` pairs of task indices. Indices refer to the deterministic chunks returned by the selected handler's planner. Use the same `input_ref` and `options` you submit to estimate chunking; malformed indices, duplicate edges, and cycles are rejected. A dependent task becomes claimable only after every prerequisite completes. A terminal prerequisite failure cancels queued descendants. This is ordering only: task outputs are not injected into downstream task inputs. `GET /api/v1/jobs/{job_id}/dag` reports edges and a unit-cost critical path, not a runtime forecast.

Job submissions may include an `Idempotency-Key` header (up to 256 characters). A repeated
key with the same canonical request returns the original job; using that key with different
request content returns HTTP 409. The coordinator stores only a SHA-256 digest of the key.
The binding is removed when its parent job expires and is purged.

## Queue priority and worker capabilities

`POST /api/v1/jobs` may set integer `priority` from 0 through 10 and a list of
`required_capabilities`. Worker registration includes a declared capability list; the
claim query only assigns tasks whose requirements are a subset of that declaration. The
default worker advertises `python`. These are operator-provided labels, not hardware
attestation. The coordinator adds one priority level per `MESH_COMPUTE_PRIORITY_AGING_SECONDS`
of queue wait, with a default interval of 30 seconds; jobs at the same effective priority
continue to use per-job fairness.

## Metrics and readiness

`/health` reports process liveness; `/ready` runs `SELECT 1` against PostgreSQL.
Prometheus can scrape `/metrics` for queue depth by job and priority, workers by status,
completion/retry/failure/lease-expiry totals, and a 24-hour task-duration histogram. The
JSON `/api/v1/metrics/summary` also includes a one-minute drain hint derived from recent
completions per active worker. That hint is heuristic and should not be treated as a
capacity guarantee.

Tasks that exhaust their attempt budget are copied to the persistent dead-letter table.
Administrators can inspect a bounded page at `GET /api/v1/dead-letters`; the entry retains
the task payload and a bounded failure reason until its parent job is purged.

## Verification

Run `uv run pytest -q --cov=meshcompute --cov-fail-under=80`, `uv run alembic upgrade head && uv run alembic check`, and `docker compose config -q`. The PostgreSQL integration tests require a reachable PostgreSQL database configured by `MESH_COMPUTE_DATABASE_URL`.
