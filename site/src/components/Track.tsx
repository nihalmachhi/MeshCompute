export function Track({ value, color = "var(--ok)" }: { value: number; color?: string }) {
  return (
    <div style={{ height: 6, borderRadius: 6, background: "var(--ln)", overflow: "hidden", minWidth: 70 }}>
      <div style={{ height: "100%", width: `${Math.max(0, Math.min(100, value))}%`, background: color, borderRadius: 6 }} />
    </div>
  );
}