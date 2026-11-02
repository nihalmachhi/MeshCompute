import { faq } from "../data/faq";

export function Faq() {
  return (
    <section className="sec" id="faq">
      <div className="wrap">
        <h2>Any <i className="ico" style={{ "--c": "#ec4899" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M9.5 9a2.6 2.6 0 115 .6c0 1.8-2.5 2.2-2.5 4M12 17.5h.01"/></svg></i> <span className="m">questions?</span></h2>
        <div className="faq">
          {faq.map((f) => (
            <details key={f.q}>
              <summary>{f.q}</summary>
              <p>{f.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}