export const faq = [
  { q: "What does at-least-once mean here?", a: "Tasks may run more than once after a worker disappears; handlers must be idempotent." },
  { q: "What is a fencing token?", a: "The attempt number prevents stale workers from committing results." },
  { q: "What happens when a worker dies mid-task?", a: "The lease expires and the reaper requeues the task." },
  { q: "Why PostgreSQL as the queue?", a: "SKIP LOCKED gives durable, transactional claiming." },
  { q: "How do schedulers differ?", a: "FIFO, fair share, and shortest-job-first have different wait/fairness tradeoffs." },
  { q: "What is speculative execution?", a: "Duplicate slow tasks; first committed result wins." },
  { q: "How are images handled safely?", a: "Allow-listed handlers, path confinement, pixel limits." },
  { q: "How is duplicate detection evaluated?", a: "Precision/recall on generated transformed images." },
  { q: "Is it production ready?", a: "It is a compact reference system, not a managed queue." },
];