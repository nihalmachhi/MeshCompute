import { useState } from "react";
import { periodicityScore } from "../features/simulator/engine";

function buildBeacon(period: number, jitter: number, n: number): number[] {
  const out: number[] = [];
  for (let i = 0; i < n; i++) {
    out.push(i * period + (Math.sin(i) * jitter * period) / 100);
  }
  return out;
}

export function Simulator() {
  const [period, setPeriod] = useState(30);
  const [jitter, setJitter] = useState(5);
  const [threshold, setThreshold] = useState(0.75);
  const [n, setN] = useState(8);
  const times = buildBeacon(period, jitter, n);
  const res = periodicityScore(times);
  const fires = res.score >= threshold;
  return (
    <section className="sec" id="try">
      <div className="wrap">
        <h2 style={{ fontSize: "clamp(1.8rem,4vw,2.6rem)", letterSpacing: "-0.035em", lineHeight: 1.05, maxWidth: "18ch" }}>Deception lab</h2>
        <p style={{ marginTop: 12, color: "var(--mu)", maxWidth: "60ch" }}>Run scripted benign actors against three on-screen decoys with a TypeScript port of the session builder.</p>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 24 }}>
          <div style={{ background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 16, padding: 20 }}>
            <label>Period (s): {period}<br /><input type="range" min={5} max={120} value={period} onChange={(e) => setPeriod(+e.target.value)} /></label><br />
            <label>Jitter (%): {jitter}<br /><input type="range" min={0} max={60} value={jitter} onChange={(e) => setJitter(+e.target.value)} /></label><br />
            <label>Connections: {n}<br /><input type="range" min={4} max={20} value={n} onChange={(e) => setN(+e.target.value)} /></label><br />
            <label>Threshold: {threshold.toFixed(2)}<br /><input type="range" min={0.5} max={0.95} step={0.05} value={threshold} onChange={(e) => setThreshold(+e.target.value)} /></label>
            <button onClick={() => { setJitter(60); setPeriod(30); }} style={{ marginTop: 12, padding: "6px 12px", borderRadius: 8, border: "1px solid var(--ln)", background: "var(--p2)", color: "var(--fg)", cursor: "pointer" }}>Make it evade</button>
          </div>
          <div style={{ background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 16, padding: 20, fontFamily: "var(--fm)", fontSize: "0.85rem" }}>
            <div>score: {res.score}</div>
            <div>period_s: {res.period_s}</div>
            <div>within 10%: {res.within_ten_percent}</div>
            <div>robust_cv: {res.robust_cv}</div>
            <div style={{ marginTop: 12, color: fires ? "var(--bad)" : "var(--ok)" }}>{fires ? "Alert fires" : "No alert"}</div>
          </div>
        </div>
      </div>
    </section>
  );
}