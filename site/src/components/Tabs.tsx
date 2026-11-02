import { useState } from "react";
import { CodeBlock } from "./CodeBlock";

export function Tabs({ tabs }: { tabs: { label: string; content: string }[] }) {
  const [active, setActive] = useState(0);
  return (
    <div>
      <div role="tablist" style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        {tabs.map((t, i) => (
          <button
            key={t.label}
            role="tab"
            aria-selected={i === active}
            onClick={() => setActive(i)}
            onKeyDown={(e) => {
              if (e.key === "ArrowRight") setActive((a) => Math.min(tabs.length - 1, a + 1));
              if (e.key === "ArrowLeft") setActive((a) => Math.max(0, a - 1));
            }}
            className="pill"
          >
            {t.label}
          </button>
        ))}
      </div>
      <CodeBlock code={tabs[active].content} />
    </div>
  );
}