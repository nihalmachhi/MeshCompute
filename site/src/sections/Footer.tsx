export function Footer() {
  return (
    <footer className="wrap">
      <div className="foot">
        <div className="fcols">
          <div>
            <a className="brand" href="#top">MeshCompute</a>
            <p className="tg">A contained defensive deception and behavior analysis lab.</p>
          </div>
          <div>
            <h5>Product</h5>
            <ul><li><a href="#top">Overview</a></li><li><a href="#how">Pipeline</a></li><li><a href="#try">Simulator</a></li><li><a href="#results">Results</a></li></ul>
          </div>
          <div>
            <h5>Run it</h5>
            <ul><li><a href="#features">Features</a></li><li><a href="#start">Quick start</a></li><li><a href="#faq">FAQ</a></li></ul>
          </div>
          <div>
            <h5>Source</h5>
            <ul><li><a href="https://github.com/nihalmachhi/MeshCompute">GitHub</a></li><li><a href="https://github.com/nihalmachhi/MeshCompute/tree/main/docs">Docs</a></li><li><a href="https://github.com/nihalmachhi/MeshCompute/issues">Issues</a></li></ul>
          </div>
        </div>
        <div className="fbot">
          <span>Synthetic demo. Scores, costs and latencies are illustrative, not real model quality or provider pricing.</span>
          <span>Python · SQLite · JSON · MIT License</span>
        </div>
        <div className="mark" aria-hidden="true">MeshCompute</div>
      </div>
    </footer>
  );
}