"""PageRank over directed graphs."""


def pagerank(adjacency: dict, damping: float = 0.85, iterations: int = 20):
    nodes = set(adjacency)
    for outs in adjacency.values():
        nodes.update(outs)
    nodes = sorted(nodes)
    n = len(nodes)
    if n == 0:
        return {}
    rank = {node: 1.0 / n for node in nodes}
    for _ in range(iterations):
        new = {node: (1 - damping) / n for node in nodes}
        for u in nodes:
            outs = adjacency.get(u, [])
            if outs:
                share = rank[u] / len(outs)
                for v in outs:
                    new[v] += damping * share
        rank = new
    return rank
