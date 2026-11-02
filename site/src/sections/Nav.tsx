export function Nav() {
  return (
    <nav className="top" aria-label="Main">
      <a className="brand" href="#top">
        <img src="/readme-icon.png" alt="" width="22" height="22" /> MeshCompute
      </a>
      <div className="links">
        <a href="#how">Pipeline</a>
        <a href="#sim">Simulator</a>
        <a href="#results">Results</a>
        <a href="#features">Features</a>
        <a href="#start">Quick start</a>
        <a href="#faq">FAQ</a>
      </div>
      <div className="sp">
        <a className="pill" href="https://github.com/nihalmachhi/MeshCompute">GitHub</a>
        <a className="pill w" href="#start">Run it locally</a>
      </div>
    </nav>
  );
}