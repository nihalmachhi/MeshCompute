# Architecture and execution flow

```mermaid
flowchart LR
    UI[Next.js dashboard] -->|REST and WebSocket| API[FastAPI coordinator]
    API --> S[Job and task services]
    S --> R[Repositories and unit of work]
    R --> DB[(PostgreSQL durable queue)]
    W[Worker process] -->|claim, heartbeat, report| API
    S --> E[In-memory event hub]
    E -->|best effort| UI
    RP[Lease reaper] --> DB
```

The coordinator owns job state, scheduling, retry policy, and persistence. Workers are stateless executors: they poll the API, heartbeat while executing, and report a fenced attempt number. The task repository claims work using PostgreSQL row locks with `SKIP LOCKED`, so multiple coordinators can claim concurrently without a separate broker.

## Task lifecycle

```mermaid
stateDiagram-v2
    [*] --> PENDING
    PENDING --> RUNNING: worker claim
    RUNNING --> COMPLETED: successful result
    RUNNING --> PENDING: retryable error or expired lease
    RUNNING --> FAILED: retry limit reached
    PENDING --> CANCELLED: job cancelled
    RUNNING --> CANCELLED: job cancelled
```

Each claim increments the attempt number and sets an expiring lease. Heartbeats extend the lease. The reaper detects expired attempts and requeues or fails them. A stale attempt cannot commit after a later attempt has been claimed. Delivery is at least once; handlers should be deterministic/idempotent.

The API accepts registered handler names and structured data only. WebSocket events speed up dashboard refresh, while PostgreSQL remains authoritative.
