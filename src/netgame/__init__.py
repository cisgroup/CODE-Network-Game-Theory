from .player import Attacker, Builder, Defender, Operator, Player, User


def hello() -> str:
    return "Hello from netgame!"


__all__ = [
    "Player",
    "Attacker",
    "Defender",
    "Builder",
    "Operator",
    "User",
    "hello",
]
