export function Pipeline() {
  const steps = [
    { title: "Split", text: "A job becomes durable tasks with byte-aware chunking." },
    { title: "Lease", text: "Workers claim tasks via PostgreSQL row locks." },
    { title: "Merge", text: "Partial results aggregate into one answer." },
  ];
  return (
    <section>
      <h2>Pipeline</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 16 }}>
        {steps.map((s) => (
          <div key={s.title} className="card">
            <h3>{s.title}</h3>
            <p style={{ color: "var(--mu)" }}>{s.text}</p>
          </div>
        ))}
      </div>
    </section>
  );
}