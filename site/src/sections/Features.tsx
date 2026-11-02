import { content } from "../data/content";

export function Features() {
  return (
    <section className="sec" id="features">
      <h2>Features</h2>
      <div className="bento">
        {content.features.map((f) => (
          <div className="bc" key={f}>
            <h3>{f}</h3>
          </div>
        ))}
        <div className="bc f">
          <h3>Not in this release</h3>
          <p>Exactly-once execution, arbitrary user code, multi-region, GPU scheduling.</p>
        </div>
      </div>
    </section>
  );
}