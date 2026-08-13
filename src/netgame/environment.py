from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

try:
    import networkx as nx
except Exception:  # networkx is optional; loaders will check
    nx = None


def _parse_csv_id(value: Optional[str]) -> Optional[Any]:
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    # try integer
    try:
        return int(value)
    except Exception:
        pass
    # try float
    try:
        return float(value)
    except Exception:
        pass
    return value


class Environment:
    def __init__(
        self,
        name: str,
        capacity: int = 100,
        resources: int = 0,
        size: tuple[int, int] = (5, 5),
        *,
        source: Optional[Any] = None,
        source_type: str = "test",
    ):
        """Create an Environment.

        Parameters
        - name: environment name
        - resources: environment resources
        - capacity, resources: legacy args kept for compatibility
        - size: used for grid generation when `source_type` is "test"
        - source: optional source for other types (networkx.Graph instance or path)
        - source_type: one of "test", "networkx", "geojson", "csv"
        """
        self.name = name
        self.capacity = capacity
        self.resources = resources
        self.size = size

        # mapping from external labels to contiguous integer indices used internally
        self.label_to_idx: Dict[Any, int] = {}
        self.idx_to_label: Dict[int, Any] = {}

        if source_type == "test" or source is None:
            self.adjacency: Dict[int, Set[int]] = self._make_test_grid(*size)
            # identity mapping for grid
            self.label_to_idx = {i: i for i in self.adjacency.keys()}
            self.idx_to_label = {i: i for i in self.adjacency.keys()}
        elif source_type == "networkx":
            if nx is None:
                raise RuntimeError("networkx is required to load networkx graphs")
            self.adjacency = self._from_networkx(source)
        elif source_type == "geojson":
            self.adjacency = self._from_geojson(Path(source))
        elif source_type == "csv":
            # `source` can be a tuple (nodes_csv, edges_csv) or a single edges csv path
            if isinstance(source, (list, tuple)):
                nodes_csv, edges_csv = source[0], source[1]
            else:
                nodes_csv, edges_csv = None, source
            self.adjacency = self._from_csv(nodes_csv and Path(nodes_csv), Path(edges_csv))
        else:
            raise ValueError(f"unknown source_type: {source_type}")

        self.nodes: Set[int] = set(self.adjacency.keys())

    def _make_test_grid(self, rows: int, cols: int) -> Dict[int, Set[int]]:
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

    def _from_networkx(self, G: Any) -> Dict[int, Set[int]]:
        if nx is None:
            raise RuntimeError("networkx not available")
        # map graph nodes to contiguous ints
        nodes = list(G.nodes())
        self.label_to_idx = {label: i for i, label in enumerate(nodes)}
        self.idx_to_label = {i: label for label, i in self.label_to_idx.items()}
        adjacency: Dict[int, Set[int]] = {i: set() for i in range(len(nodes))}
        for u in nodes:
            ui = self.label_to_idx[u]
            for v in G.neighbors(u):
                vi = self.label_to_idx[v]
                adjacency[ui].add(vi)
        return adjacency

    def _from_csv(self, nodes_path: Optional[Path], edges_path: Path) -> Dict[int, Set[int]]:
        # Read nodes if provided (expect header with 'id'), otherwise infer from edges
        nodes: List[Any] = []
        if nodes_path is not None and nodes_path.exists():
            with nodes_path.open(newline="") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    nodes.append(_parse_csv_id(row.get("id") or row.get("node") or row.get("label")))
        # read edges
        edges: List[Tuple[Any, Any]] = []
        with edges_path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                s = _parse_csv_id(row.get("source") or row.get("u") or row.get("from"))
                t = _parse_csv_id(row.get("target") or row.get("v") or row.get("to"))
                if s is None or t is None:
                    # try positional columns
                    vals = list(row.values())
                    if len(vals) >= 2:
                        s = _parse_csv_id(vals[0])
                        t = _parse_csv_id(vals[1])
                if s is not None and t is not None:
                    edges.append((s, t))

        if not nodes:
            # infer nodes from edges
            node_set = set()
            for s, t in edges:
                node_set.add(s)
                node_set.add(t)
            nodes = sorted(node_set)

        self.label_to_idx = {label: i for i, label in enumerate(nodes)}
        self.idx_to_label = {i: label for label, i in self.label_to_idx.items()}
        adjacency: Dict[int, Set[int]] = {i: set() for i in range(len(nodes))}
        for s, t in edges:
            si = self.label_to_idx[s]
            ti = self.label_to_idx[t]
            adjacency[si].add(ti)
            adjacency[ti].add(si)
        return adjacency

    def _from_geojson(self, path: Path) -> Dict[int, Set[int]]:
        data = json.loads(path.read_text())
        nodes: List[Any] = []
        coords_to_label: Dict[Tuple[float, float], Any] = {}

        features = data.get("features") if isinstance(data, dict) else None
        if features is None:
            raise ValueError("geojson must contain a FeatureCollection with features")

        # collect point features as nodes
        for feat in features:
            geom = feat.get("geometry", {})
            props = feat.get("properties", {})
            if geom.get("type") == "Point":
                coord = tuple(geom.get("coordinates", ()))
                label = props.get("id", props.get("name", None))
                if label is None:
                    label = coord
                nodes.append(label)
                coords_to_label[coord] = label

        # collect edges from LineString features or from properties
        edges: List[Tuple[Any, Any]] = []
        for feat in features:
            geom = feat.get("geometry", {})
            props = feat.get("properties", {})
            if geom.get("type") == "LineString":
                # try source/target in properties
                if "source" in props and "target" in props:
                    edges.append((props["source"], props["target"]))
                else:
                    coords = geom.get("coordinates", [])
                    if len(coords) >= 2:
                        a = coords_to_label.get(tuple(coords[0]))
                        b = coords_to_label.get(tuple(coords[-1]))
                        if a is not None and b is not None:
                            edges.append((a, b))

        if not nodes:
            # fallback: use unique labels found in edges
            node_set = set()
            for s, t in edges:
                node_set.add(s)
                node_set.add(t)
            nodes = sorted(node_set)

        self.label_to_idx = {label: i for i, label in enumerate(nodes)}
        self.idx_to_label = {i: label for label, i in self.label_to_idx.items()}
        adjacency: Dict[int, Set[int]] = {i: set() for i in range(len(nodes))}
        for s, t in edges:
            si = self.label_to_idx[s]
            ti = self.label_to_idx[t]
            adjacency[si].add(ti)
            adjacency[ti].add(si)
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
