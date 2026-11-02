export function IconChip({ color, children }: { color: string; children: React.ReactNode }) {
  return (
    <div
      style={{
        width: 46,
        height: 46,
        borderRadius: 14,
        background: color,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        marginBottom: 18,
        color: "#fff",
      }}
    >
      {children}
    </div>
  );
}