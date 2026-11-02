export function Pipeline() {
  const steps = [
    { title: "Split", text: "A job becomes durable tasks with byte-aware chunking." },
    { title: "Lease", text: "Workers claim tasks via PostgreSQL row locks." },
    { title: "Merge", text: "Partial results aggregate into one answer." },
  ];
  return (
    <div className="g3">
      {steps.map((s) => (
        <div key={s.title}>
          <h3>{s.title}</h3>
          <p>{s.text}</p>
        </div>
      ))}
    </div>
  );
}