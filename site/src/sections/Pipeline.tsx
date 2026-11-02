export function Pipeline() {
  const steps = [
    { title: "1. Decoy", body: "Inert web admin, SSH-like and fake DB services run on an isolated network. Anything that touches them is suspicious by definition.", color: "#8b5cf6", mini: "decoy › request › event" },
    { title: "2. Capture", body: "Credentials are reduced to a user class and length plus a keyed hash. Raw passwords are never stored.", color: "#f59e0b", mini: "password → [REDACTED]" },
    { title: "3. Classify", body: "Events link into sessions, sessions into actors, and rules map behavior to ATT&CK with evidence.", color: "#f97316", mini: "rule fired · tactic · technique" },
  ];
  return (
    <section className="sec" id="how">
      <div className="wrap">
        <h2>Three steps. <span className="m">One <i className="ico" style={{ "--c": "#22c55e" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></i> deception trail.</span></h2>
        <p className="lead2">Every touch becomes an event, and every event is scored against transparent rules.</p>
        <div className="steps">
          {steps.map((s) => (
            <div className="step" key={s.title}>
              <div className="ib" style={{ "--c": s.color } as React.CSSProperties}>
                <svg viewBox="0 0 24 24"><path d="M5 7h14M5 12h14M5 17h14"/></svg>
              </div>
              <h3>{s.title}</h3>
              <p>{s.body}</p>
              <div className="mini"><b>{s.mini}</b></div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}