from __future__ import annotations


class Player:
    def __init__(self, name: str, capacity: int = 100, resources: int = 0, role: str = "Player", knowledge: int = 100):
        self.name = name
        self.capacity = capacity
        self.resources = resources
        self.role = role
        self.knowledge = knowledge

    def act(self) -> str:
        return f"{self.name} is ready to play as a {self.role}."

    def status(self) -> dict[str, int | str]:
        return {
            "name": self.name,
            "role": self.role,
            "capacity": self.capacity,
            "resources": self.resources,
            "knowledge": self.knowledge,
        }

    def __str__(self) -> str:
        return f"I am {self.name}, the {self.role}, with {self.knowledge} knowledge at {self.capacity} capacity and {self.resources} resources."


class Attacker(Player):
    def __init__(self, name: str, capacity: int = 100, resources: int = 0, knowledge: int = 0, attack_power: int = 25):
        super().__init__(name, capacity, resources, role="Attacker", knowledge=knowledge)
        self.attack_power = attack_power

    def act(self) -> str:
        return f"{self.name} attacks with power {self.attack_power}."


class Defender(Player):
    def __init__(self, name: str, capacity: int = 100, resources: int = 0, knowledge: int = 100, defense_power: int = 25):
        super().__init__(name, capacity, resources, role="Defender", knowledge=knowledge)
        self.defense_power = defense_power

    def act(self) -> str:
        return f"{self.name} defends with shield strength {self.defense_power}."


class Builder(Player):
    def __init__(self, name: str, capacity: int = 100, resources: int = 0, knowledge: int = 100, build_speed: int = 10):
        super().__init__(name, capacity, resources, role="Builder", knowledge=knowledge)
        self.build_speed = build_speed

    def act(self) -> str:
        return f"{self.name} builds structures at speed {self.build_speed}."


class Operator(Player):
    def __init__(self, name: str, capacity: int = 100, resources: int = 0, knowledge: int = 100, control_level: int = 10):
        super().__init__(name, capacity, resources, role="Operator", knowledge=knowledge)
        self.control_level = control_level

    def act(self) -> str:
        return f"{self.name} operates systems with control level {self.control_level}."


class User(Player):
    def __init__(self, name: str, capacity: int = 100, resources: int = 0, knowledge: int = 100, experience: int = 5):
        super().__init__(name, capacity, resources, role="User", knowledge=knowledge)
        self.experience = experience

    def act(self) -> str:
        return f"{self.name} participates as a user with experience {self.experience}."