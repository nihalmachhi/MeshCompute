export function Scope() {
  return (
    <section>
      <h2>Scope</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div className="card">
          <strong>In scope</strong>
          <p>Compact PostgreSQL-backed distributed task processor.</p>
        </div>
        <div className="card">
          <strong>Out of scope</strong>
          <p>Exactly-once side effects, arbitrary user code, GPU scheduling.</p>
        </div>
      </div>
    </section>
  );
}