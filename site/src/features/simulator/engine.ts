export type SchedulerName = "fifo" | "fair" | "sjf";

export interface Task {
  task_id: number;
  job_id: string;
  duration: number;
  arrival: number;
}

export interface Job {
  job_id: string;
  tasks: Task[];
}

export interface SimulationResult {
  makespan: number;
  mean_wait: number;
  p95_wait: number;
  utilization: number;
  fairness: number;
  tasks: number;
  retries: number;
  schedule: {
    task_id: number;
    job_id: string;
    worker: number;
    start: number;
    end: number;
    success: boolean;
  }[];
}

export class Mulberry32 {
  private state: number;

  constructor(seed: number) {
    this.state = seed >>> 0;
  }

  random(): number {
    this.state = (this.state + 0x6d2b79f5) >>> 0;
    const t = Math.imul(this.state ^ (this.state >>> 15), 1 | this.state) >>> 0;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }
}

export function makeWorkload(seed = 42, numJobs = 6, tasksPerJob = 8): Job[] {
  const random = new Mulberry32(seed);
  let taskId = 0;
  return Array.from({ length: numJobs }, (_, jobIndex) => {
    const jobId = "job-" + jobIndex;
    const size = tasksPerJob * (jobIndex === 0 ? 4 : 1);
    const tasks = Array.from({ length: size }, () => {
      const duration = 1 + random.random() * (jobIndex === 0 ? 5 : 2);
      const task: Task = {
        task_id: taskId,
        job_id: jobId,
        duration,
        arrival: 0,
      };
      taskId += 1;
      return task;
    });
    return { job_id: jobId, tasks };
  });
}

function selectTasks(
  pending: Task[],
  idle: number[],
  scheduler: SchedulerName,
): Task[] {
  const ordered = [...pending];
  if (scheduler === "fifo") {
    ordered.sort((a, b) => a.arrival - b.arrival || a.task_id - b.task_id);
    return ordered.slice(0, idle.length);
  }
  if (scheduler === "sjf") {
    ordered.sort(
      (a, b) =>
        a.duration - b.duration ||
        a.arrival - b.arrival ||
        a.task_id - b.task_id,
    );
    return ordered.slice(0, idle.length);
  }
  const jobs = [...new Set(ordered.map((task) => task.job_id))].sort();
  const selected: Task[] = [];
  while (selected.length < idle.length) {
    let progressed = false;
    for (const jobId of jobs) {
      const next = ordered
        .filter((task) => task.job_id === jobId)
        .sort((a, b) => a.arrival - b.arrival || a.task_id - b.task_id)[0];
      if (next) {
        selected.push(next);
        ordered.splice(ordered.indexOf(next), 1);
        progressed = true;
        if (selected.length === idle.length) break;
      }
    }
    if (!progressed) break;
  }
  return selected;
}

function rounded(value: number): number {
  return Math.round(value * 1000) / 1000;
}

export function simulate(
  jobs: Job[],
  numWorkers: number,
  schedulerName: SchedulerName,
  killWorker = false,
): SimulationResult {
  const remaining = jobs.flatMap((job) =>
    job.tasks.map((task) => ({ ...task })),
  );
  const workerAvailable = Array.from({ length: numWorkers }, () => 0);
  const taskEnd = new Map<number, number>();
  const taskStart = new Map<number, number>();
  const completedByJob = new Map(jobs.map((job) => [job.job_id, 0]));
  const totalTasks = remaining.length;
  let completed = 0;
  let inFlight: {
    end: number;
    worker: number;
    task: Task;
    attempt: SimulationResult["schedule"][number];
  }[] = [];
  const schedule: SimulationResult["schedule"] = [];
  let busyTime = 0;
  let retries = 0;
  let now = 0;
  let killed = false;
  let killTime: number | null = null;

  while (completed < totalTasks) {
    const idle = workerAvailable
      .map((availableAt, worker) => ({ availableAt, worker }))
      .filter(({ availableAt }) => availableAt <= now + 1e-9)
      .map(({ worker }) => worker);

    if (idle.length > 0 && remaining.length > 0) {
      const batch = selectTasks(remaining, idle, schedulerName);
      batch.forEach((task, index) => {
        remaining.splice(remaining.indexOf(task), 1);
        const worker = idle[index]!;
        const start = Math.max(now, workerAvailable[worker]!);
        const end = start + task.duration;
        taskStart.set(task.task_id, start);
        taskEnd.set(task.task_id, end);
        workerAvailable[worker] = end;
        const attempt = {
          task_id: task.task_id,
          job_id: task.job_id,
          worker,
          start,
          end,
          success: true,
        };
        schedule.push(attempt);
        inFlight.push({ end, worker, task, attempt });
      });
      continue;
    }

    if (inFlight.length === 0 && remaining.length === 0) break;
    if (inFlight.length === 0) break;
    const nextCompletion = Math.min(...inFlight.map(({ end }) => end));
    if (
      killWorker &&
      !killed &&
      now < 2 &&
      nextCompletion >= 2 &&
      workerAvailable.length > 0
    ) {
      now = 2;
      killed = true;
      killTime = now;
      const deadWorker = workerAvailable.length - 1;
      const retry = inFlight.filter((item) => item.worker === deadWorker);
      inFlight = inFlight.filter((item) => item.worker !== deadWorker);
      for (const item of retry) {
        item.attempt.success = false;
        item.attempt.end = now;
        busyTime += Math.max(0, now - item.attempt.start);
        remaining.push(item.task);
        retries += 1;
      }
      workerAvailable.pop();
      continue;
    }
    now = nextCompletion;
    const still: typeof inFlight = [];
    for (const item of inFlight) {
      if (item.end <= now + 1e-9) {
        completed += 1;
        busyTime += item.end - item.attempt.start;
        completedByJob.set(
          item.task.job_id,
          (completedByJob.get(item.task.job_id) ?? 0) + 1,
        );
      } else {
        still.push(item);
      }
    }
    inFlight = still;
  }

  const makespan = taskEnd.size > 0 ? Math.max(...taskEnd.values()) : 0;
  const waits = jobs.flatMap((job) =>
    job.tasks.map((task) => (taskStart.get(task.task_id) ?? 0) - task.arrival),
  );
  const sortedWaits = [...waits].sort((a, b) => a - b);
  const meanWait =
    waits.length > 0
      ? waits.reduce((sum, value) => sum + value, 0) / waits.length
      : 0;
  const p95Wait =
    sortedWaits.length > 0
      ? sortedWaits[Math.floor(0.95 * (sortedWaits.length - 1))]!
      : 0;
  let capacity = numWorkers * makespan;
  if (killTime !== null) capacity -= Math.max(0, makespan - killTime);
  const utilization = capacity > 0 ? Math.min(1, busyTime / capacity) : 0;
  const jobValues = [...completedByJob.values()];
  const sum = jobValues.reduce((total, value) => total + value, 0);
  const sumSquares = jobValues.reduce(
    (total, value) => total + value * value,
    0,
  );
  const fairness =
    sumSquares > 0 ? (sum * sum) / (jobValues.length * sumSquares) : 0;

  return {
    makespan: rounded(makespan),
    mean_wait: rounded(meanWait),
    p95_wait: rounded(p95Wait),
    utilization: rounded(utilization),
    fairness: rounded(fairness),
    tasks: totalTasks,
    retries,
    schedule,
  };
}
