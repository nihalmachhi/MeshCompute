import { describe, expect, it } from "vitest";
import fixture from "./__fixtures__/cluster.json";
import {
  makeWorkload,
  simulate,
  type Job,
} from "./engine";

describe("cluster simulator parity", () => {
  it("builds the same seeded task mix as Python", () => {
    expect(makeWorkload(fixture.seed, fixture.jobs.length, 8)).toEqual(fixture.jobs);
  });

  for (const scheduler of ["fifo", "fair", "sjf"] as const) {
    it("matches Python " + scheduler + " runs and failure recovery", () => {
      const jobs = fixture.jobs as Job[];
      const expected = fixture.expected[scheduler];
      expect(simulate(jobs, fixture.workers, scheduler)).toEqual(expected.normal);
      expect(simulate(jobs, fixture.workers, scheduler, true)).toEqual(
        expected.worker_failure,
      );
    });
  }

  it("recovers a killed worker task and keeps utilization bounded", () => {
    const jobs: Job[] = [
      {
        job_id: "long-job",
        tasks: Array.from({ length: 4 }, (_, task_id) => ({
          task_id,
          job_id: "long-job",
          duration: 6,
          arrival: 0,
        })),
      },
    ];
    const recovered = simulate(jobs, 2, "fifo", true);
    expect(recovered.retries).toBe(1);
    expect(recovered.makespan).toBeGreaterThan(12);
    expect(recovered.utilization).toBeLessThanOrEqual(1);
    expect(recovered.schedule.filter((item) => !item.success)).toHaveLength(1);
  });
});
