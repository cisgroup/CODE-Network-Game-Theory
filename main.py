import json
import random
from typing import Any, Dict, Iterable, Set

from netgame import Attacker, Defender


def make_grid_graph(m: int, n: int) -> Dict[int, Set[int]]:
    adj: Dict[int, Set[int]] = {i: set() for i in range(m * n)}
    def idx(x: int, y: int) -> int:
        return x * n + y

    for x in range(m):
        for y in range(n):
            u = idx(x, y)
            if x > 0:
                adj[u].add(idx(x - 1, y))
            if x < m - 1:
                adj[u].add(idx(x + 1, y))
            if y > 0:
                adj[u].add(idx(x, y - 1))
            if y < n - 1:
                adj[u].add(idx(x, y + 1))
    return adj


def connected_components(adj: Dict[int, Set[int]]) -> Iterable[Set[int]]:
    seen: Set[int] = set()
    for node in adj.keys():
        if node in seen:
            continue
        comp: Set[int] = set()
        stack = [node]
        while stack:
            v = stack.pop()
            if v in seen:
                continue
            seen.add(v)
            comp.add(v)
            for w in adj.get(v, ()):  # neighbors
                if w not in seen:
                    stack.append(w)
        yield comp


def largest_cc_size(adj: Dict[int, Set[int]]) -> int:
    comps = list(connected_components(adj))
    if not comps:
        return 0
    return max(len(c) for c in comps)


def betweenness_centrality(adj: Dict[int, Set[int]]) -> Dict[int, float]:
    # Brandes algorithm for unweighted graphs
    nodes = list(adj.keys())
    CB = {v: 0.0 for v in nodes}
    for s in nodes:
        S: list[int] = []
        P: Dict[int, list[int]] = {w: [] for w in nodes}
        sigma = {w: 0 for w in nodes}
        dist = {w: -1 for w in nodes}
        sigma[s] = 1
        dist[s] = 0
        queue = [s]
        while queue:
            v = queue.pop(0)
            S.append(v)
            for w in adj[v]:
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    P[w].append(v)
        delta = {w: 0.0 for w in nodes}
        while S:
            w = S.pop()
            for v in P[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w]) if sigma[w] != 0 else 0
            if w != s:
                CB[w] += delta[w]
    return CB


def run_game(seed: int | None = 42) -> dict[str, Any]:
    random.seed(seed)

    # Environment: 5x5 lattice/grid
    adj = make_grid_graph(5, 5)
    nodes = set(adj.keys())

    # Players
    defender = Defender(name="Engineer", capacity=150, resources=50, defense_power=30)
    attacker = Attacker(name="Storm", capacity=120, resources=40, attack_power=35)

    results: dict[str, Any] = {
        "initial_nodes": len(nodes),
        "lcc_sizes": [],
        "removed_order": [],
    }

    results["lcc_sizes"].append(largest_cc_size(adj))

    step = 0
    while nodes:
        step += 1

        # Defender computes betweenness on current graph
        centrality = betweenness_centrality({v: {w for w in adj[v] if w in nodes} for v in nodes})
        if centrality:
            target = max(centrality, key=centrality.get)
            protected = {target} | {n for n in adj[target] if n in nodes}
        else:
            protected = set()

        # Attacker selects a random unprotected node
        candidates = [n for n in nodes if n not in protected]
        if not candidates:
            results["removed_order"].append(None)
            results["lcc_sizes"].append(largest_cc_size({v: {w for w in adj[v] if w in nodes} for v in nodes}))
            break

        choice = random.choice(candidates)
        # remove node
        nodes.remove(choice)
        results["removed_order"].append(choice)
        # compute lcc size on remaining nodes
        results["lcc_sizes"].append(largest_cc_size({v: {w for w in adj[v] if w in nodes} for v in nodes}))

    results["steps"] = step
    return results


def main():
    results = run_game()
    print("Run finished. Steps:", results.get("steps"))
    print("Largest connected component sizes:", results.get("lcc_sizes"))

    # save results
    with open("game_results.json", "w") as fh:
        json.dump(results, fh, indent=2)


if __name__ == "__main__":
    main()
