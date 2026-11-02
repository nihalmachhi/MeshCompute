import { useMemo, useState } from "react";
import {
  makeWorkload,
  simulate,
  type SchedulerName,
} from "../features/simulator/engine";

const schedulers: { id: SchedulerName; label: string }[] = [
  { id: "fifo", label: "FIFO" },
  { id: "fair", label: "Fair share" },
  { id: "sjf", label: "Shortest job first" },
];

const jobColors = ["#f472b6", "#4ade9a", "#38bdf8", "#fbbf24", "#a78bfa", "#fb7185"];

export function Simulator() {
  const [workers, setWorkers] = useState(4);
  const [tasksPerJob, setTasksPerJob] = useState(8);
  const [failedWorker, setFailedWorker] = useState(false);
  const [scheduler, setScheduler] = useState<SchedulerName>("fair");
  const jobs = useMemo(() => makeWorkload(42, 6, tasksPerJob), [tasksPerJob]);
  const runs = useMemo(
    () =>
      Object.fromEntries(
        schedulers.map(({ id }) => [
          id,
          simulate(jobs, workers, id, failedWorker),
        ]),
      ) as Record<SchedulerName, ReturnType<typeof simulate>>,
    [failedWorker, jobs, workers],
  );
  const active = runs[scheduler];
  const makespan = Math.max(1, active.makespan);

  return (
    <section className="sec" id="try">
      <div className="wrap">
        <h2>Try the <span className="m">cluster lab.</span></h2>
        <p className="lead2">
          Change the worker pool, compare schedulers on the same seeded job mix, and inject a worker
          failure. Everything runs locally in your browser.
        </p>
        <div className="lab">
          <div className="lab-controls">
            <label>
              Workers <strong>{workers}</strong>
              <input
                type="range"
                min="2"
                max="8"
                value={workers}
                onChange={(event) => setWorkers(Number(event.currentTarget.value))}
              />
            </label>
            <label>
              Tasks per job <strong>{tasksPerJob}</strong>
              <input
                type="range"
                min="4"
                max="12"
                value={tasksPerJob}
                onChange={(event) => setTasksPerJob(Number(event.currentTarget.value))}
              />
            </label>
            <label className="checkline">
              <input
                type="checkbox"
                checked={failedWorker}
                onChange={(event) => setFailedWorker(event.currentTarget.checked)}
              />
              Kill a worker at 2 seconds
            </label>
            <label>
              Timeline policy
              <select
                value={scheduler}
                onChange={(event) => setScheduler(event.currentTarget.value as SchedulerName)}
              >
                {schedulers.map((item) => (
                  <option value={item.id} key={item.id}>{item.label}</option>
                ))}
              </select>
            </label>
          </div>
          <div className="lab-output" aria-live="polite">
            <div className="metric-grid">
              <div><span>MAKESPAN</span><strong>{active.makespan}s</strong></div>
              <div><span>P95 QUEUE WAIT</span><strong>{active.p95_wait}s</strong></div>
              <div><span>UTILIZATION</span><strong>{Math.round(active.utilization * 100)}%</strong></div>
              <div><span>JAIN FAIRNESS</span><strong>{active.fairness}</strong></div>
            </div>
            <div className="compare-grid">
              {schedulers.map((item) => (
                <button
                  className={scheduler === item.id ? "compare-card selected" : "compare-card"}
                  key={item.id}
                  onClick={() => setScheduler(item.id)}
                  type="button"
                >
                  <span>{item.label}</span>
                  <strong>{runs[item.id].makespan}s</strong>
                  <small>p95 wait {runs[item.id].p95_wait}s · fairness {runs[item.id].fairness}</small>
                </button>
              ))}
            </div>
            <div className="gantt-wrap">
              <h3>Task timeline <span>seed 42 · {workers} workers</span></h3>
              <div className="gantt">
                {active.schedule.map((task, index) => {
                  const width = Math.max(0.4, ((task.end - task.start) / makespan) * 100);
                  const left = (task.start / makespan) * 100;
                  return (
                    <div className="gantt-row" key={index}>
                      <span>W{task.worker + 1}</span>
                      <div className="gantt-track">
                        <i
                          className={task.success ? "" : "failed-attempt"}
                          style={{
                            left: left + "%",
                            width: width + "%",
                            backgroundColor: task.success
                              ? jobColors[Number(task.job_id.slice(4)) % jobColors.length]
                              : "var(--bad)",
                          }}
                          title={task.job_id + " · task " + task.task_id + (task.success ? "" : " · retried")}
                        />
                      </div>
                      <small>{task.job_id}</small>
                    </div>
                  );
                })}
              </div>
              <p className="note">
                Seeded synthetic workload. The failure run retries an interrupted task; it does not
                model network or database performance.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
