import { useEffect, useState } from "react";
import { simulate } from "./engine";
import type { Task } from "./engine";
import fixture from "./__fixtures__/sim.json";

export function SimPanel() {
  const [workers, setWorkers] = useState(4);
  const [sched, setSched] = useState("fifo");
  const [result, setResult] = useState<Record<string, number> | null>(null);
  useEffect(() => {
    const tasks = (fixture as { tasks: Task[] }).tasks;
    setResult(simulate(workers, tasks, sched) as Record<string, number>);
  }, [workers, sched]);
  return (
    <div className="card">
      <label>
        Workers{" "}
        <input type="number" value={workers} onChange={(e) => setWorkers(Number(e.target.value))} />
      </label>
      <select value={sched} onChange={(e) => setSched(e.target.value)}>
        <option value="fifo">FIFO</option>
        <option value="fair">Fair</option>
        <option value="sjf">SJF</option>
      </select>
      {result && (
        <div aria-live="polite" style={{ marginTop: 12, fontFamily: "var(--fm)", fontSize: 13 }}>
          makespan: {result.makespan} | p95 wait: {result.p95_wait} | fairness: {result.fairness}
        </div>
      )}
    </div>
  );
}

export default SimPanel;