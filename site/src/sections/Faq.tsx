import { faq } from "../data/faq";
import { Disclosure } from "../components/Disclosure";

export function Faq() {
  return (
    <section>
      <h2>FAQ</h2>
      {faq.map((f) => (
        <Disclosure key={f.q} question={f.q} answer={f.a} />
      ))}
    </section>
  );
}