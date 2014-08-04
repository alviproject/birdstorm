class BattleOver(Exception):
    def __init__(self, loser):
        self.loser = loser