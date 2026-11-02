"""BFS shortest paths over adjacency lists."""

from collections import deque


def bfs(adjacency: dict, source):
    dist = {source: 0}
    q = deque([source])
    while q:
        u = q.popleft()
        for v in adjacency.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist
