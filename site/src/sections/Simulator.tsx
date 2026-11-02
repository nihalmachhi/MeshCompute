import { Suspense, lazy } from "react";
const Sim = lazy(() => import("../features/simulator/SimPanel"));

export function Simulator() {
  return (
    <section id="simulator">
      <h2>Cluster lab</h2>
      <Suspense fallback={<div>Loading simulator…</div>}>
        <Sim />
      </Suspense>
    </section>
  );
}