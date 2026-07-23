from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Player:
    name: str
    capacity: int = 100
    resources: int = 0
    role: str = field(init=False, default="Player")

    def act(self) -> str:
        return f"{self.name} is ready to play as a {self.role}."

    def status(self) -> dict[str, int | str]:
        return {
            "name": self.name,
            "role": self.role,
            "capacity": self.capacity,
            "resources": self.resources,
        }

    def __str__(self) -> str:
        return f"I am the {self.role}(name={self.name} at {self.capacity} capacity and {self.resources} resources)"


@dataclass(slots=True)
class Attacker(Player):
    attack_power: int = 25
    role: str = field(init=False, default="Attacker")

    def act(self) -> str:
        return f"{self.name} attacks with power {self.attack_power}."


@dataclass(slots=True)
class Defender(Player):
    defense_power: int = 25
    role: str = field(init=False, default="Defender")

    def act(self) -> str:
        return f"{self.name} defends with shield strength {self.defense_power}."


@dataclass(slots=True)
class Builder(Player):
    build_speed: int = 10
    role: str = field(init=False, default="Builder")

    def act(self) -> str:
        return f"{self.name} builds structures at speed {self.build_speed}."


@dataclass(slots=True)
class Operator(Player):
    control_level: int = 10
    role: str = field(init=False, default="Operator")

    def act(self) -> str:
        return f"{self.name} operates systems with control level {self.control_level}."


@dataclass(slots=True)
class User(Player):
    experience: int = 5
    role: str = field(init=False, default="User")

    def act(self) -> str:
        return f"{self.name} participates as a user with experience {self.experience}."