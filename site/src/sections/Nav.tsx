import { content } from "../data/content";

export function Nav() {
  return (
    <nav className="top" aria-label="Main">
      <div className="wrap" style={{ display: "flex", alignItems: "center", gap: 26, width: "100%" }}>
        <a className="brand" href="#top">
          <img src="/readme-icon.png" alt="MeshCompute" width={22} height={22} />
          {content.name}
        </a>
        <div className="links">
          {content.nav.links.map((l) => (
            <a key={l.href} href={l.href}>{l.label}</a>
          ))}
        </div>
        <div className="sp">
          <a className="pill" href="https://github.com/nihalmachhi/MeshCompute">GitHub</a>
          <a className="pill w" href="#start">Run it locally</a>
        </div>
      </div>
    </nav>
  );
}