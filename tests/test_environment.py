import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netgame.environment import Environment


def test_lattice_environment_tracks_components_and_removals():
    env = Environment(name="Roads", capacity=200, resources=100, size=(3, 3))

    assert env.node_count() == 9
    assert env.largest_connected_component_size() == 9

    env.remove_node(0)
    assert env.node_count() == 8
    assert env.largest_connected_component_size() == 8
