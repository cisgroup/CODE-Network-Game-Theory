from __future__ import annotations

import random
from typing import Any, Dict, List

from .environment import Environment
from .player import Attacker, Defender


class Game:
    def __init__(self, environment: Environment, defender: Defender, attacker: Attacker, seed: int | None = 42):
        self.environment = environment
        self.defender = defender
        self.attacker = attacker
        self.seed = seed

    def defender_action(self) -> set[int]:
        centrality = self.environment.betweenness_centrality()
        if centrality:
            target = max(centrality, key=centrality.get)
            return {target} | self.environment.neighbors(target)
        return set()

    def attacker_action(self, protected: set[int]) -> int | None:
        candidates = [node for node in sorted(self.environment.nodes) if node not in protected]
        if not candidates:
            return None
        return random.choice(candidates)

    def run(self) -> Dict[str, Any]:
        random.seed(self.seed)

        results: Dict[str, Any] = {
            "initial_nodes": self.environment.node_count(),
            "lcc_sizes": [],
            "removed_order": [],
            "steps": 0,
            "players": [self.defender.status(), self.attacker.status()],
        }

        results["lcc_sizes"].append(self.environment.largest_connected_component_size())

        while self.environment.node_count() > 0:
            results["steps"] += 1

            protected = self.defender_action()
            choice = self.attacker_action(protected)
            if choice is None:
                results["removed_order"].append(None)
                results["lcc_sizes"].append(self.environment.largest_connected_component_size())
                break

            self.environment.remove_node(choice)
            results["removed_order"].append(choice)
            results["lcc_sizes"].append(self.environment.largest_connected_component_size())

        return results


__all__ = ["Game"]
