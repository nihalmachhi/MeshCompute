export type JobStatus = "SUBMITTED" | "RUNNING" | "COMPLETED" | "FAILED";
export type WorkerStatus = "ACTIVE" | "STALE" | "OFFLINE";
export interface JobView { id: string; job_type: string; status: JobStatus; task_count: number; tasks_by_state: Record<string, number>; created_at: string; finished_at: string | null; }
export interface WorkerView { worker_id: string; name: string; status: WorkerStatus; last_heartbeat_at: string; heartbeat_age_seconds: number; current_task_id: string | null; }
export interface TaskView { task_id: string; task_index: number; status: string; attempt: number; max_attempts: number; worker_id: string | null; lease_expires_at: string | null; queued_at: string; started_at: string | null; finished_at: string | null; }
export interface Metrics { workers: { active: number; stale: number }; queue_size: number; completed_last_minute: number; retries: number; failures: number; mean_task_duration_ms: number; }
export interface JobPage { items: JobView[]; limit: number; offset: number; }
