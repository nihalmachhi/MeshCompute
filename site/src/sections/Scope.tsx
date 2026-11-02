export function Scope() {
  return (
    <section className="sec" id="scope">
      <div className="wrap">
        <h2>Built to <span className="m">teach systems trade-offs.</span></h2>
        <p className="lead2">MeshCompute is an educational distributed task processor, not a general-purpose cloud compute platform.</p>
        <div className="sc">
          <article className="scc">
            <div className="ib good"><span aria-hidden="true">+</span></div>
            <h3>In scope</h3>
            <ul><li>Registered task handlers</li><li>Leased, fenced attempts</li><li>PostgreSQL-backed coordination</li><li>Seeded scheduler simulations</li><li>Graph, text, and image exercises</li></ul>
          </article>
          <article className="scc">
            <div className="ib bad"><span aria-hidden="true">−</span></div>
            <h3>Out of scope</h3>
            <ul><li>Exactly-once side effects</li><li>Arbitrary submitted code</li><li>GPU scheduling</li><li>Multi-region control plane</li><li>Production throughput claims</li></ul>
          </article>
        </div>
      </div>
    </section>
  );
}
