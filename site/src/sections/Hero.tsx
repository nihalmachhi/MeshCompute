import { Window } from "../components/Window";

export function Hero() {
  return (
    <section style={{ textAlign: "center" }}>
      <h1>Split big work. Survive failure. Merge the answer.</h1>
      <p style={{ color: "var(--mu)", maxWidth: 720, margin: "0 auto" }}>
        MeshCompute breaks a job into durable tasks, leases them to workers, recovers work when a worker disappears, and merges the results, with schedulers you can compare on the same workload.
      </p>
      <div style={{ display: "flex", gap: 12, justifyContent: "center", marginTop: 20 }}>
        <a href="#quickstart" className="pill primary">
          Run it locally
        </a>
        <a href="https://github.com/nihalmachhi/MeshCompute" className="pill">
          GitHub
        </a>
      </div>
      <div style={{ marginTop: 32 }}>
        <Window>
          <p style={{ fontFamily: "var(--fm)", fontSize: 13 }}>Submit → Plan → Claim → Recover → Merge</p>
        </Window>
      </div>
    </section>
  );
}