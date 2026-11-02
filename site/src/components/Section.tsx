import type { ReactNode } from "react";

export function Section({ children, id }: { children: ReactNode; id?: string }) {
  return <section id={id}>{children}</section>;
}