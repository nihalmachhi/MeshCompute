export const faq = [
  { q: "What does at-least-once execution mean?", a: "A task can be attempted again when a worker disappears or its lease expires. Fenced, idempotent commits prevent an old attempt from overwriting a newer result." },
  { q: "What is an attempt fence?", a: "Each task claim increments an attempt number. The coordinator accepts results only from the currently assigned worker and attempt." },
  { q: "What happens when a worker dies?", a: "The lease reaper can return expired work to the queue, subject to the task retry limit. The simulator shows a simplified version of that recovery." },
  { q: "Why use PostgreSQL as a queue?", a: "Transactions and row-level locks coordinate claims across coordinator processes without introducing a separate broker in this learning project." },
  { q: "How do the schedulers differ?", a: "FIFO follows enqueue order, fair share rotates work between jobs, and shortest-job-first uses the task duration available to the simulator." },
  { q: "Does the browser lab call a server?", a: "No. It runs a seeded TypeScript simulator locally in the browser and sends no task inputs or files." },
  { q: "Can I submit arbitrary code?", a: "No. Job types resolve to a registered handler; clients cannot send Python, shell commands, or executable functions." },
  { q: "Are the results production benchmarks?", a: "No. The generated values come from a deterministic synthetic workload and describe simulator behavior only." },
  { q: "Is MeshCompute production ready?", a: "No. It is an educational prototype. It does not promise exactly-once side effects, GPU scheduling, or a multi-region control plane." },
];
