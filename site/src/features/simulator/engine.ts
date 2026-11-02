export function mulberry32(seed: number): () => number {
  let state = seed >>> 0;
  return function () {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = (state ^ (state >>> 15)) * (1 | state);
    t >>>= 0;

    return (((t ^ (t >>> 14)) >>> 0) / 4294967296);
  };
}

export type Task = { task_id: number; job_id: string; duration: number; arrival: number };

export function simulate(numWorkers: number, tasks: Task[], scheduler: string, killWorker: boolean = false) {
  const remaining = tasks.map((t) => ({ ...t }));
  let workerAvailable = Array.from({ length: numWorkers }, () => 0);
  const taskStart: Record<number, number> = {};
  const taskEnd: Record<number, number> = {};
  const completedByJob: Record<string, number> = {};
  for (const t of tasks) completedByJob[t.job_id] = 0;
  let completed = 0;
  const total = tasks.length;
  const inFlight: { end: number; w: number; task: Task }[] = [];
  let now = 0;
  let killed = false;

  function pickBatch(pending: Task[], idleCount: number): Task[] {
    if (scheduler === "sjf") {
      return [...pending].sort((a, b) => a.duration - b.duration || a.arrival - b.arrival || a.task_id - b.task_id).slice(0, idleCount);
    }
    if (scheduler === "fair") {
      const jobCounts: Record<string, number> = {};
      for (const t of pending) jobCounts[t.job_id] = (jobCounts[t.job_id] || 0) + 1;
      const orderedJobs = Object.keys(jobCounts).sort();
      const result: Task[] = [];
      const remaining2 = [...pending];
      for (let i = 0; i < idleCount; i++) {
        let progressed = false;
        for (const job of orderedJobs) {
          const cand = remaining2.filter((t) => t.job_id === job);
          if (cand.length) {
            const chosen = cand.reduce((a, b) => (a.arrival < b.arrival || (a.arrival === b.arrival && a.task_id < b.task_id) ? a : b));
            result.push(chosen);
            const idx = remaining2.indexOf(chosen);
            remaining2.splice(idx, 1);
            progressed = true;
            if (result.length >= idleCount) break;
          }
        }
        if (!progressed || result.length >= idleCount) break;
      }
      return result;
    }
    // fifo
    return [...pending].sort((a, b) => a.arrival - b.arrival || a.task_id - b.task_id).slice(0, idleCount);
  }

  while (completed < total) {
    const idle = workerAvailable.map((v, i) => (v <= now + 1e-9 ? i : -1)).filter((i) => i >= 0);
    if (idle.length > 0 && remaining.length > 0) {
      const batch = pickBatch(remaining, idle.length);
      for (let k = 0; k < batch.length; k++) {
        const task = batch[k];
        const w = idle[k];
        const idx = remaining.indexOf(task);
        if (idx >= 0) remaining.splice(idx, 1);
        const start = Math.max(now, workerAvailable[w]);
        const end = start + task.duration;
        taskStart[task.task_id] = start;
        taskEnd[task.task_id] = end;
        workerAvailable[w] = end;
        inFlight.push({ end, w, task });
      }
      continue;
    }
    if (inFlight.length === 0) break;
    const nextTime = Math.min(...inFlight.map((x) => x.end));
    now = nextTime;
    const still: typeof inFlight = [];
    for (const item of inFlight) {
      if (item.end <= now + 1e-9) {
        completed += 1;
        completedByJob[item.task.job_id] = (completedByJob[item.task.job_id] || 0) + 1;
      } else {
        still.push(item);
      }
    }
    // kill worker
    if (killWorker && !killed && now >= 2.0) {
      killed = true;
      const toRequeue = inFlight.filter((x) => x.w === workerAvailable.length - 1).map((x) => x.task);
      const filtered = inFlight.filter((x) => x.w !== workerAvailable.length - 1);
      inFlight.length = 0;
      inFlight.push(...filtered);
      for (const t of toRequeue) remaining.push(t);
      workerAvailable = workerAvailable.slice(0, -1);
    }
    inFlight.length = 0;
    inFlight.push(...still);
  }

  const makespan = Math.max(...Object.values(taskEnd));
  const waits = tasks.map((t) => taskStart[t.task_id] - t.arrival);
  const meanWait = waits.reduce((a, b) => a + b, 0) / waits.length;
  const sortedWaits = [...waits].sort((a, b) => a - b);
  const p95 = sortedWaits[Math.floor(0.95 * (sortedWaits.length - 1))];
  const totalWork = tasks.reduce((a, t) => a + t.duration, 0);
  const util = totalWork / ((workerAvailable.length || 1) * makespan);
  const jobValues = Object.values(completedByJob);
  const ssum = jobValues.reduce((a, b) => a + b, 0);
  const sq = jobValues.reduce((a, b) => a + b * b, 0);
  const n = jobValues.length;
  const jain = sq > 0 ? (ssum * ssum) / (n * sq) : 0;
  return {
    makespan: +makespan.toFixed(3),
    mean_wait: +meanWait.toFixed(3),
    p95_wait: +p95.toFixed(3),
    utilization: +util.toFixed(3),
    fairness: +jain.toFixed(3),
    tasks: total,
  };
}