export function Results() {
  return (
    <section className="sec" id="results">
      <div className="wrap">
        <h2>Compared on the <span className="m">same <i className="ico" style={{ "--c": "#06b6d4" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M7 19v-6M12 19V6M17 19v-10"/></svg></i> scripted actors.</span></h2>
        <p className="lead2">Scripted lab actors, not real attackers. These numbers show the workflow, not real-world detection.</p>
        <div className="rg">
          <div className="rc">
            <h3>Classifier</h3>
            <p>Precision and recall per label from the generated evaluation.</p>
            <div className="tb">
              <div className="mr"><span>Task</span><div className="track"><div className="grow" style={{ "--w": "90%", "--c": "#8c8c95" } as React.CSSProperties} /></div><b>90%</b></div>
            </div>
          </div>
          <div className="rc">
            <h3>Containment</h3>
            <p>The list of controls and pass/fail from the checker.</p>
            <div className="tb">
              <div className="mr"><span>Controls</span><div className="track"><div className="grow" style={{ "--w": "100%", "--c": "var(--ok)" } as React.CSSProperties} /></div><b>pass</b></div>
            </div>
          </div>
          <div className="rc">
            <h3>Integrity</h3>
            <p>Chain verification results incl. the tamper test.</p>
            <div className="tb">
              <div className="mr"><span>Chain</span><div className="track"><div className="grow" style={{ "--w": "100%", "--c": "#a78bfa" } as React.CSSProperties} /></div><b>valid</b></div>
            </div>
          </div>
        </div>
        <p className="note">Scripted lab actors, not real attackers. These numbers show the workflow, not real-world detection.</p>
      </div>
    </section>
  );
}