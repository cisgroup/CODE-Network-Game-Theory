import json
from typing import Any

from netgame import Attacker, Defender, Environment, Game


def run_game(seed: int | None = 42) -> dict[str, Any]:
    environment = Environment(name="Lattice Grid", capacity=200, resources=100, size=(5, 5), source = None, source_type = "test")
    defender = Defender(name="Engineer", capacity=150, resources=50, knowledge = 100, defense_power=30)
    attacker = Attacker(name="Storm", capacity=120, resources=40, knowledge = 0, attack_power=35)
    game = Game(environment=environment, defender=defender, attacker=attacker, seed=seed)
    return game.run()


def main():
    results = run_game()
    print("Run finished. Steps:", results.get("steps"))
    print("Largest connected component sizes:", results.get("lcc_sizes"))

    # save results
    with open("game_results.json", "w") as fh:
        json.dump(results, fh, indent=2)


if __name__ == "__main__":
    main()
