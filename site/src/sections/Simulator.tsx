import { Suspense, lazy } from "react";
const Sim = lazy(() => import("../features/simulator/SimPanel"));

export function Simulator() {
  return (
    <div className="sim">
      <Suspense fallback={<div>Loading simulator…</div>}>
        <Sim />
      </Suspense>
    </div>
  );
}