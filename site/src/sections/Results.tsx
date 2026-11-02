import results from "../data/results.generated.json";

export function Results() {
  return (
    <section className="sec" id="results">
      <h2>Compared on the same workload.</h2>
      <div className="rg">
        {Object.entries(results).map(([k, v]: [string, { makespan: number; p95_wait: number; fairness: number }]) => (
          <div className="rc" key={k}>
            <h3>{k}</h3>
            <p>Makespan {v.makespan}, p95 wait {v.p95_wait}, fairness {v.fairness}.</p>
          </div>
        ))}
      </div>
      <p className="note">Simulated cluster and generated data.</p>
    </section>
  );
}