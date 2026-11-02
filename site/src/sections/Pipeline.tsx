const steps = [
  {
    title: "Submit and plan",
    body: "A registered handler turns an input into bounded, durable tasks. PostgreSQL records the job before workers can claim it.",
    color: "#f472b6",
    mini: "job → task 0 · task 1 · task 2",
  },
  {
    title: "Lease and fence",
    body: "Workers claim tasks with a time-limited lease. Each attempt number fences off stale completions after a retry.",
    color: "#38bdf8",
    mini: "worker-2 · attempt 3 · lease 30s",
  },
  {
    title: "Recover and merge",
    body: "Expired work returns to the queue. Once every task result is committed, the coordinator combines the partial outputs.",
    color: "#4ade9a",
    mini: "retry → fenced result → aggregate",
  },
];

export function Pipeline() {
  return (
    <section className="sec" id="how">
      <div className="wrap">
        <h2>Three stages. <span className="m">One durable job.</span></h2>
        <p className="lead2">Tasks can run more than once; leases and fencing protect the committed result.</p>
        <div className="steps">
          {steps.map((step, index) => (
            <article className="step" key={step.title}>
              <div className="ib" style={{ "--c": step.color } as React.CSSProperties}>
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d={index === 0 ? "M5 5h14v4H5zM5 15h14v4H5zM8 7h.01M8 17h.01" : index === 1 ? "M12 3 20 6v5c0 5-3 8-8 10-5-2-8-5-8-10V6z" : "M5 12.5l4.5 4.5L19 7.5"} />
                </svg>
              </div>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
              <div className="mini"><b>{step.mini}</b></div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
