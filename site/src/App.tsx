import { Nav } from "./sections/Nav";
import { Hero } from "./sections/Hero";
import { Pipeline } from "./sections/Pipeline";
import { Simulator } from "./sections/Simulator";
import { Results } from "./sections/Results";
import { Features } from "./sections/Features";
import { QuickStart } from "./sections/QuickStart";
import { Scope } from "./sections/Scope";
import { Faq } from "./sections/Faq";
import { Cta } from "./sections/Cta";
import { Footer } from "./sections/Footer";

export default function App() {
  return (
    <>
      <a className="skip-link" href="#main">Skip to content</a>
      <Nav />
      <main id="main">
        <Hero />
        <Pipeline />
        <Simulator />
        <Results />
        <Features />
        <QuickStart />
        <Scope />
        <Faq />
        <Cta />
      </main>
      <Footer />
    </>
  );
}