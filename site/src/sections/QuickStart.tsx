import { Tabs } from "../components/Tabs";

export function QuickStart() {
  const bash = "uv sync --extra dev\ncp .env.example .env\ndocker compose up --build";
  const ps = "uv sync --extra dev\ncopy .env.example .env\ndocker compose up --build";
  return (
    <section id="quickstart">
      <h2>Quick start</h2>
      <Tabs tabs={[{ label: "bash", content: bash }, { label: "PowerShell", content: ps }]} />
    </section>
  );
}