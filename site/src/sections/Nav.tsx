export function Nav() {
  return (
    <nav style={{ height: 72, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <img src="/readme-icon.png" alt="MeshCompute" width={32} height={32} />
        <strong>MeshCompute</strong>
      </div>
      <div style={{ display: "flex", gap: 12 }}>
        <a href="#quickstart" className="pill">
          Run it locally
        </a>
        <a href="https://github.com/nihalmachhi/MeshCompute" className="pill">
          GitHub
        </a>
      </div>
    </nav>
  );
}