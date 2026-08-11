from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Set


class Environment:
    def __init__(self, name: str, capacity: int, resources: int, size: tuple[int, int] = (5, 5)):
        self.name = name
        self.capacity = capacity
        self.resources = resources
        self.size = size
        self.adjacency: Dict[int, Set[int]] = self._make_grid_graph(*size)
        self.nodes: Set[int] = set(self.adjacency.keys())

    def _make_grid_graph(self, rows: int, cols: int) -> Dict[int, Set[int]]:
        adjacency: Dict[int, Set[int]] = {i: set() for i in range(rows * cols)}

        def idx(r: int, c: int) -> int:
            return r * cols + c

        for r in range(rows):
            for c in range(cols):
                u = idx(r, c)
                if r > 0:
                    adjacency[u].add(idx(r - 1, c))
                if r < rows - 1:
                    adjacency[u].add(idx(r + 1, c))
                if c > 0:
                    adjacency[u].add(idx(r, c - 1))
                if c < cols - 1:
                    adjacency[u].add(idx(r, c + 1))
        return adjacency

    def node_count(self) -> int:
        return len(self.nodes)

    def remove_node(self, node: int) -> None:
        if node in self.nodes:
            self.nodes.remove(node)

    def neighbors(self, node: int) -> Set[int]:
        return {neighbor for neighbor in self.adjacency.get(node, set()) if neighbor in self.nodes}

    def connected_components(self) -> Iterable[Set[int]]:
        seen: Set[int] = set()
        for node in sorted(self.nodes):
            if node in seen:
                continue
            component: Set[int] = set()
            stack = [node]
            while stack:
                current = stack.pop()
                if current in seen:
                    continue
                seen.add(current)
                component.add(current)
                for neighbor in self.neighbors(current):
                    if neighbor not in seen:
                        stack.append(neighbor)
            yield component

    def largest_connected_component_size(self) -> int:
        components = list(self.connected_components())
        if not components:
            return 0
        return max(len(component) for component in components)

    def betweenness_centrality(self) -> Dict[int, float]:
        nodes = sorted(self.nodes)
        if not nodes:
            return {}

        centrality = {node: 0.0 for node in nodes}
        for source in nodes:
            stack: List[int] = []
            predecessors: Dict[int, List[int]] = {node: [] for node in nodes}
            sigma = {node: 0.0 for node in nodes}
            distance = {node: -1 for node in nodes}
            sigma[source] = 1.0
            distance[source] = 0
            queue = [source]

            while queue:
                current = queue.pop(0)
                stack.append(current)
                for neighbor in self.neighbors(current):
                    if distance[neighbor] < 0:
                        distance[neighbor] = distance[current] + 1
                        queue.append(neighbor)
                    if distance[neighbor] == distance[current] + 1:
                        sigma[neighbor] += sigma[current]
                        predecessors[neighbor].append(current)

            dependency = {node: 0.0 for node in nodes}
            while stack:
                w = stack.pop()
                for v in predecessors[w]:
                    dependency[v] += (sigma[v] / sigma[w]) * (1.0 + dependency[w]) if sigma[w] != 0.0 else 0.0
                if w != source:
                    centrality[w] += dependency[w]

        return centrality

    def status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "capacity": self.capacity,
            "resources": self.resources,
            "size": self.size,
            "node_count": self.node_count(),
            "largest_component": self.largest_connected_component_size(),
        }


__all__ = ["Environment"]
