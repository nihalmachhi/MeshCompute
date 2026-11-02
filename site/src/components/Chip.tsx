export function Chip({ children, color }: { children: React.ReactNode; color?: string }) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 10px",
        borderRadius: 999,
        border: `1px solid ${color ?? "var(--ln)"}`,
        fontFamily: "var(--fm)",
        fontSize: "0.78rem",
        margin: "0 6px 6px 0",
        color: color ?? "var(--mu)",
      }}
    >
      {children}
    </span>
  );
}