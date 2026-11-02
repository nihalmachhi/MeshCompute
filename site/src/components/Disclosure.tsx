import { useState } from "react";

export function Disclosure({ question, answer }: { question: string; answer: string }) {
  const [open, setOpen] = useState(false);
  return (
    <details open={open} onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}>
      <summary style={{ cursor: "pointer", fontWeight: 600, fontFamily: "var(--fd)", fontSize: "1.05rem" }}>
        {question}
      </summary>
      <p style={{ marginTop: 8, color: "var(--mu)", maxWidth: "68ch", fontSize: "0.95rem" }}>{answer}</p>
    </details>
  );
}