import type { ReactNode } from "react";

export function IconChip({ children }: { children: ReactNode }) {
  return (
    <span
      style={{
        display: "inline-flex",
        width: 32,
        height: 32,
        alignItems: "center",
        justifyContent: "center",
        borderRadius: 8,
        background: "var(--p2)",
        border: "1px solid var(--ln)",
        color: "var(--accent)",
      }}
    >
      {children}
    </span>
  );
}