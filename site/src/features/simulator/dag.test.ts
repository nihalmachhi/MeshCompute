import { describe, expect, it } from "vitest";
import { canAddEdge, criticalPath, type DagEdge } from "./dag";

describe("interactive DAG planner", () => {
  it("computes the longest dependency path and fixed-duration ETA", () => {
    const result = criticalPath([["map", "shuffle"], ["shuffle", "reduce"]]);
    expect(result).toEqual({ path: ["map", "shuffle", "reduce"], seconds: 9 });
  });

  it("prevents a cycle while permitting a shortcut edge", () => {
    const edges: DagEdge[] = [["map", "shuffle"], ["shuffle", "reduce"]];
    expect(canAddEdge(edges, ["map", "reduce"])).toBe(true);
    expect(canAddEdge(edges, ["reduce", "map"])).toBe(false);
  });
});
