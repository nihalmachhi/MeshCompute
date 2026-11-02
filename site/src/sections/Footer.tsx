export function Footer() {
  return (
    <footer className="card" style={{ marginTop: 40 }}>
      <img src="/readme-icon.png" alt="MeshCompute" width={32} height={32} />
      <p>MIT License</p>
      <p style={{ background: "linear-gradient(180deg,#f4f4f5 15%,#2c2c31 88%)", WebkitBackgroundClip: "text", color: "transparent", fontSize: "4rem" }}>
        MeshCompute
      </p>
    </footer>
  );
}