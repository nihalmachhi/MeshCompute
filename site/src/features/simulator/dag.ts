export const stages = [
  { id: "map", label: "Map", duration: 3 },
  { id: "shuffle", label: "Shuffle", duration: 2 },
  { id: "reduce", label: "Reduce", duration: 4 },
] as const;

export type StageId = (typeof stages)[number]["id"];
export type DagEdge = readonly [StageId, StageId];

export function canAddEdge(edges: readonly DagEdge[], edge: DagEdge): boolean {
  const [from, to] = edge;
  if (from === to) return false;
  const adjacency = new Map<StageId, StageId[]>();
  for (const [source, target] of edges) {
    adjacency.set(source, [...(adjacency.get(source) ?? []), target]);
  }
  const visited = new Set<StageId>();
  const pending = [to];
  while (pending.length) {
    const current = pending.pop()!;
    if (current === from) return false;
    if (visited.has(current)) continue;
    visited.add(current);
    pending.push(...(adjacency.get(current) ?? []));
  }
  return true;
}

export function criticalPath(edges: readonly DagEdge[]) {
  const indegree = new Map<StageId, number>(stages.map(({ id }) => [id, 0]));
  const adjacency = new Map<StageId, StageId[]>(stages.map(({ id }) => [id, []]));
  for (const [from, to] of edges) {
    adjacency.get(from)!.push(to);
    indegree.set(to, indegree.get(to)! + 1);
  }
  const order: StageId[] = [];
  const ready = stages.map(({ id }) => id).filter((id) => indegree.get(id) === 0);
  const cost = new Map<StageId, number>();
  const parent = new Map<StageId, StageId | null>();
  while (ready.length) {
    const current = ready.shift()!;
    order.push(current);
    const stage = stages.find(({ id }) => id === current)!;
    const predecessor = edges
      .filter(([, target]) => target === current)
      .map(([source]) => source)
      .sort((left, right) => (cost.get(right)! - cost.get(left)!))[0];
    cost.set(current, stage.duration + (predecessor ? cost.get(predecessor)! : 0));
    parent.set(current, predecessor ?? null);
    for (const child of adjacency.get(current)!) {
      indegree.set(child, indegree.get(child)! - 1);
      if (indegree.get(child) === 0) ready.push(child);
    }
  }
  if (order.length !== stages.length) return { path: [] as StageId[], seconds: 0 };
  let end = order.reduce((best, id) => (cost.get(id)! > cost.get(best)! ? id : best));
  const path: StageId[] = [];
  while (end) {
    path.unshift(end);
    const previous = parent.get(end);
    if (previous === null || previous === undefined) break;
    end = previous;
  }
  return { path, seconds: cost.get(path[path.length - 1]!) ?? 0 };
}
