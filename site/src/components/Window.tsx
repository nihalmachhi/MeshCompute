import type { ReactNode } from "react";

export function Window({ children }: { children: ReactNode }) {
  return (
    <div
      style={{
        background: "var(--p)",
        border: "1px solid var(--ln)",
        borderRadius: 20,
        boxShadow: "0 40px 90px -40px #000",
        overflow: "hidden",
      }}
    >
      <div style={{ display: "flex", gap: 6, padding: 12, borderBottom: "1px solid var(--ln)" }}>
        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "#ff5f57" }} />
        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "#febc2e" }} />
        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "#28c840" }} />
      </div>
      <div style={{ padding: 16 }}>{children}</div>
    </div>
  );
}