import type { JobPage, JobView, Metrics, TaskView, WorkerView } from "@/lib/types";
const baseUrl = process.env.NEXT_PUBLIC_COORDINATOR_URL ?? "http://localhost:8000/api/v1";
async function request<T>(path: string): Promise<T> { const response = await fetch(baseUrl + path, { cache: "no-store" }); if (!response.ok) throw new Error("Coordinator returned " + response.status); return response.json() as Promise<T>; }
export function loadJobs(): Promise<JobPage> { return request("/jobs?limit=50"); }
export function loadWorkers(): Promise<WorkerView[]> { return request("/workers"); }
export function loadMetrics(): Promise<Metrics> { return request("/metrics/summary"); }
export function loadJob(jobId: string): Promise<JobView> { return request("/jobs/" + jobId); }
export function loadTasks(jobId: string): Promise<TaskView[]> { return request("/jobs/" + jobId + "/tasks"); }
export function eventSocketUrl(): string { const url = new URL(baseUrl); url.protocol = url.protocol === "https:" ? "wss:" : "ws:"; url.pathname = "/api/v1/ws/events"; return url.toString(); }
