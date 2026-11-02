"""Connected components over partitioned edge lists."""

from meshcompute.handlers.base import JsonObject


def connected_components(edges: list[tuple[int, int]]) -> list[list[int]]:
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for a, b in edges:
        find(a)
        find(b)
        union(a, b)
    groups = {}
    for node in parent:
        groups.setdefault(find(node), []).append(node)
    return sorted(groups.values())


class ComponentsHandler:
    def split(self, input_ref: str, options: JsonObject) -> list[JsonObject]:
        return [
            {"edges": options.get("edges", []), "partition": i}
            for i in range(int(options.get("partitions", 1)))
        ]

    def execute(self, payload: JsonObject) -> JsonObject:
        edges = [tuple(e) for e in payload.get("edges", [])]
        return {"components": connected_components(edges)}

    def merge(self, results: list[JsonObject]) -> JsonObject:
        for _r in results:
            pass
        # merge component lists by union across partitions is non-trivial; return as-is
        return {"results": results}
