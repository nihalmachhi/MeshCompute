export function Architecture() {
  return (
    <section>
      <h2>Architecture</h2>
      <div className="card">
        <p style={{ fontFamily: "var(--fm)", fontSize: 13 }}>
          Client → Coordinator API → Planner (DAG) → PostgreSQL queue → Scheduler → Worker (sandboxed handler) → Fenced commit → Aggregation → Dashboard
        </p>
      </div>
    </section>
  );
}