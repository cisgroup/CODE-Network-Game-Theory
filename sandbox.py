# Mock code 
import netgame as ng
import networkx as nx

defender = ng.Defender(name="Engineer", capacity=150, resources=50, defense_power=30)
attacker = ng.Attacker(name="Storm", capacity=120, resources=40, attack_power=35)
network = nx.lattice_graph(5, 5)  # Create a 5x5 lattice graph as the network

infrastructure = ng.Environment(name="Roads", capacity=200, resources=100, network=network)

game = ng.Game(players=[defender, attacker], environment=infrastructure, start = defender)

results = game.run()

ng.save_results(results, "game_results.json")
