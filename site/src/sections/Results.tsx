import results from "../data/results.generated.json";

export function Results() {
  return (
    <section>
      <h2>Results</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 16 }}>
        {Object.entries(results).map(([k, v]) => (
          <div key={k} className="card">
            <h3>{k}</h3>
            <p>makespan: {v.makespan}</p>
            <p>p95 wait: {v.p95_wait}</p>
            <p>fairness: {v.fairness}</p>
          </div>
        ))}
      </div>
      <p style={{ color: "var(--mu)", marginTop: 12 }}>
        Simulated cluster and generated data. These results show how the schedulers behave, not production throughput.
      </p>
    </section>
  );
}