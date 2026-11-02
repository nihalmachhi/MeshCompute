export function CodeBlock({ lines }: { lines: string[] }) {
  return (
    <pre
      style={{
        background: "var(--p)",
        border: "1px solid var(--ln)",
        borderRadius: 16,
        padding: 20,
        fontFamily: "var(--fm)",
        fontSize: "0.85rem",
        lineHeight: 1.8,
        overflowX: "auto",
        color: "var(--fg)",
      }}
    >
      {lines.join("\n")}
    </pre>
  );
}