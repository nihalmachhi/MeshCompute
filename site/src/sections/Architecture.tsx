export function Architecture() {
  return (
    <section className="sec" id="arch">
      <h2>Architecture</h2>
      <div className="code">Client → Coordinator API → Planner (DAG) → PostgreSQL queue → Scheduler → Worker (sandboxed handler) → Fenced commit → Aggregation → Dashboard</div>
    </section>
  );
}