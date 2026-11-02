import type { ReactNode } from "react";

export function Pill({ children, primary }: { children: ReactNode; primary?: boolean }) {
  return <span className={`pill${primary ? " primary" : ""}`}>{children}</span>;
}