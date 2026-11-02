import { useEffect, useState } from "react";
import { useTour } from "../features/tour/useTour";

const TABS = ["Decoy", "Capture", "Classify", "Map", "Contain"];

export function Window() {
  const { index, setIndex, paused, setPaused } = useTour(TABS.length, 7000);
  const [hover, setHover] = useState(false);
  const held = hover || paused;
  useEffect(() => {
    setPaused(hover);
  }, [hover, setPaused]);
  return (
    <div
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onFocus={() => setHover(true)}
      onBlur={() => setHover(false)}
      style={{ position: "relative", background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 20, overflow: "hidden", boxShadow: "0 40px 90px -40px #000", display: "grid", gridTemplateColumns: "200px 1fr", minHeight: 440, marginTop: 28 }}
    >
      <aside style={{ borderRight: "1px solid var(--ln)", padding: 16, fontSize: "0.85rem", color: "var(--mu)" }}>
        <div style={{ display: "flex", gap: 7, padding: "2px 8px 16px" }}>
          <i style={{ width: 11, height: 11, borderRadius: "50%", background: "#ff5f57" }} />
          <i style={{ width: 11, height: 11, borderRadius: "50%", background: "#febc2e" }} />
          <i style={{ width: 11, height: 11, borderRadius: "50%", background: "#28c840" }} />
        </div>
        {TABS.map((t, i) => (
          <button
            key={t}
            role="tab"
            aria-selected={i === index}
            onClick={() => setIndex(i)}
            onKeyDown={(e) => {
              if (e.key === "ArrowRight") setIndex((index + 1) % TABS.length);
              if (e.key === "ArrowLeft") setIndex((index - 1 + TABS.length) % TABS.length);
            }}
            style={{ display: "flex", justifyContent: "space-between", padding: "7px 9px", borderRadius: 8, width: "100%", border: 0, background: i === index ? "var(--p2)" : "transparent", color: i === index ? "var(--fg)" : "var(--mu)", cursor: "pointer", marginBottom: 2 }}
          >
            {t}
            {i === index && !held && <span style={{ position: "absolute", left: 14, right: 14, bottom: 3, height: 2, background: "var(--wh)", transform: "scaleX(0)", transformOrigin: "left", animation: "fill 7s linear forwards" }} />}
          </button>
        ))}
        <div style={{ marginTop: 18, fontSize: "0.78rem", color: "#62626b" }}>Prompt versions</div>
        <div style={{ display: "flex", alignItems: "center", gap: 9, padding: "7px 10px", background: "var(--p2)", borderRadius: 9, marginBottom: 6, fontSize: "0.88rem", marginTop: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--ok)" }} /> baseline
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 9, padding: "7px 10px", background: "var(--p2)", borderRadius: 9, fontSize: "0.88rem" }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--bad)" }} /> candidate
        </div>
      </aside>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 250px", minWidth: 0 }}>
        <div style={{ padding: 20, opacity: held ? 0.9 : 1, filter: held ? "blur(2px)" : "none", transition: "opacity .25s, filter .25s" }}>
          <h3 style={{ fontSize: "1.02rem", fontWeight: 600 }}>{TABS[index]}</h3>
          <p style={{ fontSize: "0.8rem", color: "var(--mu)", marginTop: 1 }}>Auto-playing tour</p>
          <p style={{ margin: "16px 0", fontSize: "0.93rem", color: "var(--mu)" }}>
            {index === 0 && "Inert web admin, SSH-like and fake DB services."}
            {index === 1 && "Credentials reduced to length and keyed hash."}
            {index === 2 && "Rule-based session labels with the rule that fired."}
            {index === 3 && "Labels mapped to ATT&CK tactic/technique rows."}
            {index === 4 && "Compose controls checked before and after start; panic."}
          </p>
          <div style={{ background: "#0a0a0b", border: "1px solid var(--ln)", borderRadius: 12, padding: 14, fontFamily: "var(--fm)", fontSize: "0.8rem", color: "var(--mu)" }}>
            {index === 0 && "decoy › request › event"}
            {index === 1 && 'password → [REDACTED]'}
            {index === 2 && "rule fired · confidence"}
            {index === 3 && "T1595.002 · T1110.001"}
            {index === 4 && "panic requires STOP GHOSTNET"}
          </div>
        </div>
        <div style={{ padding: 20, borderLeft: "1px solid var(--ln)", background: "#101012" }}>
          <h4 style={{ margin: "0 0 8px", fontSize: "0.8rem", color: "var(--mu)" }}>Totals</h4>
          <ul style={{ listStyle: "none", margin: 0, padding: 0, fontSize: "0.86rem", color: "var(--mu)" }}>
            <li style={{ padding: "7px 0", borderBottom: "1px solid var(--ln)" }}>Spans <b style={{ float: "right", color: "var(--fg)" }}>5</b></li>
            <li style={{ padding: "7px 0", borderBottom: "1px solid var(--ln)" }}>Tokens in → out <b style={{ float: "right", color: "var(--fg)" }}>9 → 8</b></li>
            <li style={{ padding: "7px 0" }}>Estimated cost <b style={{ float: "right", color: "var(--fg)" }}>$0.000187</b></li>
          </ul>
        </div>
      </div>
      <button
        onClick={() => setPaused(!paused)}
        aria-label={paused ? "Resume the automatic tour" : "Pause the automatic tour"}
        style={{ position: "absolute", right: 16, top: 16, width: 34, height: 34, borderRadius: "50%", border: "1px solid var(--ln)", background: "var(--p)", color: "var(--mu)", cursor: "pointer" }}
      >
        {paused ? "▶" : "❚❚"}
      </button>
    </div>
  );
}