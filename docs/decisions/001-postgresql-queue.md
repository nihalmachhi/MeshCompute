# Decision 001: PostgreSQL is the durable queue

**Status:** Accepted

Use PostgreSQL 16 as both system of record and task queue. Transactions, durability, and row-level locking keep the deployable footprint small. Claims select pending tasks with `FOR UPDATE SKIP LOCKED`.

A broker becomes justified when dispatch volume outgrows database polling. It would add operational cost and dual-write/reconciliation concerns, so it is not introduced without measurements.
