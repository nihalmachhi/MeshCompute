import report from "../data/results.generated.json";

export function Results() {
  const entries = Object.entries(report.scheduler_comparison);
  const vision = report.handler_evaluation.vision_duplicate_detection;
  const text = report.handler_evaluation.text_duplicate_detection;
  const chunking = report.handler_evaluation.chunk_size_optimization;
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
        <h3>Generated duplicate detection</h3>
        <div className="rg">
          {[{ label: "Image pairs · dHash", metrics: vision }, { label: "Text pairs · MinHash", metrics: text }].map(({ label, metrics }) => (
            <article className="rc" key={label}>
              <h3>{label}</h3>
              <p>{metrics.method}</p>
              <div className="metric-grid">
                <div><span>PRECISION</span><strong>{Math.round(metrics.precision * 100)}%</strong></div>
                <div><span>RECALL</span><strong>{Math.round(metrics.recall * 100)}%</strong></div>
                <div><span>PAIRS</span><strong>{metrics.pairs}</strong></div>
              </div>
              <small>{metrics.true_positives} matches · {metrics.false_positives} false positives · {metrics.false_negatives} missed</small>
            </article>
          ))}
        </div>
        <article className="rc chunk-model">
          <h3>Chunk-size model</h3>
          <p>Generated estimate for an 8 MiB input on four workers; fixed overhead and throughput are model assumptions.</p>
          <div className="metric-grid">
            <div><span>CHUNK SIZE</span><strong>{Math.round(chunking.chunk_size_bytes / 1024)} KiB</strong></div>
            <div><span>TASK COUNT</span><strong>{chunking.task_count}</strong></div>
            <div><span>MODELED ETA</span><strong>{chunking.estimated_makespan_seconds}s</strong></div>
          </div>
        </article>
        <p className="note">{report.note}</p>
        <p className="note">The handler evaluation uses small generated inputs and does not represent general image or language understanding.</p>
      </div>
    </section>
  );
}
