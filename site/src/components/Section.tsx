import type { ReactNode } from "react";

export function Section({ id, children }: { id: string; children: ReactNode }) {
  return (
    <section id={id} style={{ padding: "84px 0 20px" }}>
      <div className="wrap">{children}</div>
    </section>
  );
}