import { describe, it, expect } from "vitest";
import fixture from "./__fixtures__/sim.json";
import { simulate } from "./engine";

describe("parity", () => {
  it("matches python fixture", () => {
    const tasks = (fixture as { tasks: { task_id: number; job_id: string; duration: number; arrival: number }[] }).tasks;
    const res = simulate(4, tasks, "fifo");
    expect(res.makespan).toBe((fixture as { expected_fifo: { makespan: number } }).expected_fifo.makespan);
  });
});