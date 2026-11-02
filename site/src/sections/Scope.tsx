export function Scope() {
  return (
    <section className="sec" id="scope">
      <div className="wrap">
        <h2>Built to <i className="ico" style={{ "--c": "#f97316" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M9 18h6M10 21h4M12 3a6 6 0 00-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0012 3z"/></svg></i> <span className="m">teach.</span></h2>
        <p className="lead2">MeshCompute is for learning how deception and behavior analysis work. It is not a production security tool.</p>
        <div className="sc">
          <div className="scc">
            <div className="ib" style={{ "--c": "#22c55e" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div>
            <h3>In scope</h3>
            <ul><li>Low-interaction decoys</li><li>Privacy-minimized events</li><li>Tamper-evident chain</li><li>Session/actor analysis</li><li>ATT&CK mapping</li><li>Contained lab network</li><li>Policy-gated adaptation proposals</li></ul>
          </div>
          <div className="scc">
            <div className="ib" style={{ "--c": "#ef4444" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></div>
            <h3>Out of scope</h3>
            <ul><li>Real shells or SQL execution</li><li>Internet-facing deployment</li><li>Offensive tooling</li><li>High-interaction honeypots</li><li>Attributing real people</li></ul>
          </div>
        </div>
      </div>
    </section>
  );
}