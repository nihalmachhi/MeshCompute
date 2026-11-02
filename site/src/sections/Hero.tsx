import { content } from "../data/content";
import { Window } from "../components/Window";

export function Hero() {
  return (
    <header className="hero" id="top">
      <h1>{content.hero.headline}</h1>
      <p>{content.hero.subcopy}</p>
      <div className="cta">
        <a className="pill w" href="#start">Run it locally</a>
        <a className="pill" href="https://github.com/nihalmachhi/MeshCompute">View on GitHub</a>
      </div>
      <div className="wrap">
        <Window />
      </div>
    </header>
  );
}