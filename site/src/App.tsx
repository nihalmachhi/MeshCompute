import "./styles/tokens.css";
import "./styles/base.css";
import { Nav } from "./sections/Nav";
import { Hero } from "./sections/Hero";
import { Pipeline } from "./sections/Pipeline";
import { Simulator } from "./sections/Simulator";
import { Results } from "./sections/Results";
import { Features } from "./sections/Features";
import { Architecture } from "./sections/Architecture";
import { QuickStart } from "./sections/QuickStart";
import { Scope } from "./sections/Scope";
import { Faq } from "./sections/Faq";
import { Cta } from "./sections/Cta";
import { Footer } from "./sections/Footer";

export default function App() {
  return (
    <div className="wrap">
      <Nav />
      <Hero />
      <section className="sec" id="how">
        <h2>Pipeline</h2>
        <Pipeline />
      </section>
      <section className="sec" id="sim">
        <h2>Cluster lab</h2>
        <Simulator />
      </section>
      <Results />
      <Features />
      <Architecture />
      <QuickStart />
      <Scope />
      <Faq />
      <Cta />
      <Footer />
    </div>
  );
}