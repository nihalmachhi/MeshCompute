export function Scope() {
  return (
    <section className="sec" id="scope">
      <h2>Scope</h2>
      <div className="sc">
        <div className="scc">
          <h3>In scope</h3>
          <ul>
            <li>Compact PostgreSQL-backed distributed task processor</li>
          </ul>
        </div>
        <div className="scc">
          <h3>Out of scope</h3>
          <ul>
            <li>Exactly-once side effects, arbitrary user code, GPU scheduling</li>
          </ul>
        </div>
      </div>
    </section>
  );
}