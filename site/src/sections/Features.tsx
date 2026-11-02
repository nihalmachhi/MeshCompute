const cards = [
  { title: "Inert decoys", body: "No real shell or SQL execution.", span: "bc w", color: "#8b5cf6", tags: ["web admin", "SSH-like", "fake DB"], icon: "M5 12h14" },
  { title: "Contained network", body: "Decoys only on internal networks.", span: "bc w", color: "#f97316", tags: ["internal: true", "edge proxy"], icon: "M8 8l-4 4 4 4M16 8l4 4-4 4" },
  { title: "Tamper-evident chain", body: "HMAC hash chain with checkpoints.", span: "bc", color: "#f59e0b", tags: ["HMAC", "checkpoints"], icon: "M12 3l7 3v5c0 5-3 8-7 10-4-2-7-5-7-10V6z" },
  { title: "Privacy-minimized capture", body: "User class and length, keyed hashes.", span: "bc", color: "#22c55e", tags: ["no raw passwords"], icon: "M5 12.5l4.5 4.5L19 7.5" },
  { title: "Transparent rules + ATT&CK", body: "Rule-based labels with evidence.", span: "bc", color: "#fafafa", tags: ["YAML rules", "ATT&CK"], icon: "M8 8l-4 4 4 4M16 8l4 4-4 4" },
  { title: "Actor graph", body: "Sessions linked into actors.", span: "bc w", color: "#ec4899", tags: ["networkx", "sessions"], icon: "M5 6c0-1.7 3.1-3 7-3s7 1.3 7 3-3.1 3-7 3-7-1.3-7-3zM5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6" },
  { title: "Policy-gated adaptation", body: "Proposes, never deploys.", span: "bc w", color: "#ef4444", tags: ["bandit", "approve"], icon: "M7 19v-6M12 19V6M17 19v-10" },
  { title: "Panic switch", body: "Stops all decoys immediately.", span: "bc", color: "#06b6d4", tags: ["STOP GHOSTNET"], icon: "M5 12h14" },
  { title: "Exports", body: "Navigator, STIX, CSV/JSONL.", span: "bc", color: "#a78bfa", tags: ["STIX 2.1"], icon: "M5 12h14" },
  { title: "Not in this release", body: "High-interaction services, public deployment, real shells.", span: "bc f", color: "#22c55e", tags: ["out of scope"], icon: "M5 12h14" },
];

export function Features() {
  return (
    <section className="sec" id="features">
      <div className="wrap">
        <h2>A small system. <span className="m">Built to be <i className="ico" style={{ "--c": "#8b5cf6" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9zM12 12l8-4.5M12 12v9M12 12L4 7.5"/></svg></i> inspected.</span></h2>
        <p className="lead2">The decoys, sensors, pipeline, admin API and dashboard each live in their own module.</p>
        <div className="bento">
          {cards.map((c) => (
            <div className={c.span} key={c.title}>
              <div className="ib" style={{ "--c": c.color } as React.CSSProperties}>
                <svg viewBox="0 0 24 24"><path d={c.icon} /></svg>
              </div>
              <h3>{c.title}</h3>
              <p>{c.body}</p>
              <div className="tags">
                {c.tags.map((t) => <span key={t}>{t}</span>)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}