export function Track({ value }: { value: number }) {
  return (
    <div style={{ height: 6, background: "var(--ln)", borderRadius: 99 }}>
      <div style={{ width: `${value}%`, height: "100%", background: "var(--accent)", borderRadius: 99 }} />
    </div>
  );
}