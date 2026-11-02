const stages = ["Decoys", "Edge proxy", "Ingest API", "Event store", "Sessions", "Rules", "ATT&CK", "Admin API", "Dashboard"];

export function Cta() {
  const boxWidth = 112;
  const gap = 30;
  return (
    <section className="cta2" aria-label="Get started">
      <div className="wrap">
        <div style={{ overflowX: "auto", padding: "6px 4px 10px", marginBottom: 24 }}>
          <svg className="flow arch" viewBox="0 0 964 90" role="img" aria-label="MeshCompute pipeline" style={{ width: "100%", minWidth: 820, maxWidth: 964, height: "auto", overflow: "visible" }}>
            {stages.map((_, i) => {
              if (i === stages.length - 1) return null;
              const x1 = i * (boxWidth + gap) + boxWidth;
              const x2 = x1 + gap;
              return <path key={i} className="fl" d={`M${x1} 45H${x2}`} style={{ fill: "none", stroke: "#5a5a64", strokeWidth: 1.2, strokeDasharray: "4 4", animation: "dash 1.2s linear infinite" }} />;
            })}
            {stages.map((s, i) => {
              const x = i * (boxWidth + gap);
              const last = i === stages.length - 1;
              return (
                <g key={s} className={`gn st ${last ? "last" : ""}`} style={{ animation: `${last ? "stlb" : "stl"} 6.3s ease-in-out infinite`, animationDelay: `${i * 0.9}s` }}>
                  <rect x={x} y={12} width={boxWidth} height={66} rx={9} style={{ fill: "#19191c", stroke: "#242428" }} />
                  <text textAnchor="middle" style={{ font: "500 10px var(--fm)", fill: "#ececee" }}>
                    {s.split(" ").map((word, wi, arr) => (
                      <tspan key={wi} x={x + boxWidth / 2} y={12 + 30 + (wi - (arr.length - 1) / 2) * 13}>
                        {word}
                      </tspan>
                    ))}
                  </text>
                </g>
              );
            })}
            <circle r={3.2} fill="#f4f4f5">
              <animateMotion dur="6.3s" repeatCount="indefinite" path="M0 45H964" />
            </circle>
          </svg>
        </div>
        <h2>Run it.<br /><span className="m">Watch it get <i className="ico pulse" style={{ "--c": "#ef4444" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M12 8v5M12 17h.01"/></svg></i> caught.</span></h2>
        <div className="btns">
          <a className="pill w" href="https://github.com/nihalmachhi/MeshCompute">View on GitHub</a>
          <a className="pill" href="#try">Back to the simulator</a>
        </div>
      </div>
    </section>
  );
}