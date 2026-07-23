import netgame as ng


def main():
    players = [
        ng.Attacker("Hurricane"),
        ng.Defender("Engineer"),
        ng.Builder("Contractor"),
        ng.Operator("Amtrak"),
        ng.User("Public"),
    ]

    for player in players:
        print(player)
        print(player.act())


if __name__ == "__main__":
    main()
