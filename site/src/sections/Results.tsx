import report from "../data/results.generated.json";

export function Results() {
  const entries = Object.entries(report.scheduler_comparison);
  const maximum = Math.max(
    ...entries.flatMap(([, runs]) => [runs.normal.makespan, runs.worker_failure.makespan]),
  );
  return (
    <section className="sec" id="results">
      <div className="wrap">
        <h2>Same workload. <span className="m">Different schedules.</span></h2>
        <p className="lead2">
          Generated with the repository’s seeded simulator. Failure recovery includes an injected
          worker loss and a retried task.
        </p>
        <div className="rg">
          {entries.map(([name, runs]) => (
            <article className="rc" key={name}>
              <h3>{name === "sjf" ? "Shortest job first" : name === "fair" ? "Fair share" : "FIFO"}</h3>
              <p>Normal run compared with the same seeded workload after a worker failure.</p>
              <div className="result-row">
                <span>Normal makespan</span>
                <div className="track"><i style={{ width: (runs.normal.makespan / maximum) * 100 + "%" }} /></div>
                <b>{runs.normal.makespan}s</b>
              </div>
              <div className="result-row">
                <span>After failure</span>
                <div className="track"><i className="failure" style={{ width: (runs.worker_failure.makespan / maximum) * 100 + "%" }} /></div>
                <b>{runs.worker_failure.makespan}s</b>
              </div>
              <small>p95 wait: {runs.normal.p95_wait}s · retries: {runs.worker_failure.retries}</small>
            </article>
          ))}
        </div>
        <p className="note">{report.note}</p>
      </div>
    </section>
  );
}
