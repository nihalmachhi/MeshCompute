import type { ReactNode } from "react";

export function Pill({ children, variant = "default" }: { children: ReactNode; variant?: "default" | "white" }) {
  const style: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    minHeight: 38,
    padding: "0 18px",
    borderRadius: 999,
    fontWeight: 500,
    fontSize: "0.9rem",
    border: "1px solid var(--ln)",
    background: variant === "white" ? "var(--wh)" : "var(--p2)",
    color: variant === "white" ? "#111" : "var(--fg)",
    cursor: "pointer",
  };
  return <span style={style}>{children}</span>;
}