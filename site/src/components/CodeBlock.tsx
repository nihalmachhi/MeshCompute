export function CodeBlock({ code }: { code: string }) {
  return (
    <pre
      style={{
        background: "var(--p)",
        border: "1px solid var(--ln)",
        borderRadius: 12,
        padding: 16,
        overflow: "auto",
        fontFamily: "var(--fm)",
        fontSize: 13,
      }}
    >
      <code>{code}</code>
    </pre>
  );
}