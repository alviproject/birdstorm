from game.apps.core.models.battle.base import BattleOver
from game.apps.core.models.battle.battle_unit import Attacker
from game.apps.core.models.battle.battle_unit import Defender


class Battlefield:
    #TODO change it to BATTLEFIELD_RADIUS and make sure that battlefield coordinates can be smaller than 0
    SIZE = 50
    BATTLE_DURATION = 50

    def __init__(self, attacker, defender):
        self._time = 0
        self.attacker = Attacker(attacker, self.time(), Battlefield.SIZE)
        self.defender = Defender(defender, self.time(), 0)

    def time(self):
        return self._time

    def process(self):
        """process a single "tick" of the battle"""
        self.attacker.process(self)
        self.defender.process(self)

    def start(self):
        result = {}
        try:
            while self.time() < Battlefield.BATTLE_DURATION:
                self.process()
                self._time += 1
        except BattleOver as x:
            result['loser'] = x.loser
        result['time'] = self._time
        return result
