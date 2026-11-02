import { describe, it, expect } from "vitest";
import { periodicityScore } from "./engine";
import fixture from "./__fixtures__/beacon.json";

describe("periodicityScore parity", () => {
  for (const [name, data] of Object.entries(fixture as Record<string, { times: number[]; result: Record<string, number> }>)) {
    it(name, () => {
      const got = periodicityScore(data.times);
      expect(got.score).toBeCloseTo(data.result.score, 6);
      expect(got.period_s).toBeCloseTo(data.result.period_s, 6);
      expect(got.within_ten_percent).toBeCloseTo(data.result.within_ten_percent, 6);
    });
  }
});