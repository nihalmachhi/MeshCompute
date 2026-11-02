import { content } from "../data/content";

export function Features() {
  return (
    <section>
      <h2>Features</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 16 }}>
        {content.features.map((f) => (
          <div key={f} className="card">
            {f}
          </div>
        ))}
        <div className="card" style={{ gridColumn: "span 3" }}>
          <strong>Not in this release</strong>: exactly-once execution, arbitrary user code, multi-region, GPU scheduling.
        </div>
      </div>
    </section>
  );
}