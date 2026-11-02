const cards = [
  { title: "Durable queue", body: "PostgreSQL row locks coordinate concurrent task claims.", span: "bc w", color: "#f472b6", tags: ["SKIP LOCKED", "leases"], icon: "M4 5h16v5H4zM4 14h16v5H4z" },
  { title: "Attempt fencing", body: "A stale attempt cannot replace a later committed result.", span: "bc", color: "#38bdf8", tags: ["attempt token"], icon: "M12 3 20 6v5c0 5-3 8-8 10-5-2-8-5-8-10V6z" },
  { title: "Scheduler lab", body: "Compare FIFO, fair-share, and SJF on the same seed.", span: "bc", color: "#4ade9a", tags: ["reproducible"], icon: "M7 19v-6M12 19V6M17 19v-10" },
  { title: "DAG planning", body: "Model dependencies, release order, and critical paths.", span: "bc", color: "#fbbf24", tags: ["map · reduce"], icon: "M5 5h5v5H5zM14 14h5v5h-5zM10 7.5h4v9h-4" },
  { title: "Allow-listed handlers", body: "Workers run registered operations instead of submitted code.", span: "bc", color: "#a78bfa", tags: ["no eval"], icon: "M5 12h14M12 5v14" },
  { title: "Graph, text, image", body: "Partition graph, catalog, and image tasks into worker-sized units.", span: "bc w", color: "#fb7185", tags: ["BFS", "TF-IDF", "BMP"], icon: "M4 6h5v5H4zM15 13h5v5h-5zM9 8.5h6v7" },
  { title: "No exactly-once claim", body: "Execution is at least once; idempotent result commits are fenced.", span: "bc f", color: "#f4f4f5", tags: ["honest scope"], icon: "M5 12h14" },
];

export function Features() {
  return (
    <section className="sec" id="features">
      <div className="wrap">
        <h2>Built to make <span className="m">failure visible.</span></h2>
        <p className="lead2">The coordinator, worker, handlers, simulator, and generated evidence are separate parts of the project.</p>
        <div className="bento">
          {cards.map((card) => (
            <article className={card.span} key={card.title}>
              <div className="ib" style={{ "--c": card.color } as React.CSSProperties}>
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d={card.icon} /></svg>
              </div>
              <h3>{card.title}</h3>
              <p>{card.body}</p>
              <div className="tags">{card.tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
