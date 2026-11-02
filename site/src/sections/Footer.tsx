export function Footer() {
  return (
    <footer className="wrap">
      <div className="foot">
        <div className="fcols">
          <div>
            <a className="brand" href="#top">
              <img src="/readme-icon.png" alt="" width="22" height="22" /> MeshCompute
            </a>
            <p className="tg">A durable distributed task processor.</p>
          </div>
        </div>
        <div className="fbot">
          <span>MIT License</span>
          <span>Python · PostgreSQL</span>
        </div>
        <div className="mark" aria-hidden="true">MeshCompute</div>
      </div>
    </footer>
  );
}