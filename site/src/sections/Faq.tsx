import { faq } from "../data/faq";

export function Faq() {
  return (
    <section className="sec" id="faq">
      <h2>FAQ</h2>
      <div className="faq">
        {faq.map((f) => (
          <details key={f.q}>
            <summary>{f.q}</summary>
            <p>{f.a}</p>
          </details>
        ))}
      </div>
    </section>
  );
}