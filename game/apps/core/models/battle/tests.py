import unittest

from game.apps.core.models.battle import Battlefield
from game.apps.core.models.battle.battle_unit import Attacker
from game.apps.core.models.battle.battle_unit import BattleShield
from game.apps.core.models.battle.battle_unit import ContinuousAction
from game.apps.core.models.battle.battle_unit import DiscreteAction
from game.apps.core.models.shields import Shield
from game.apps.core.models.ships import Ship


class TestBattle(unittest.TestCase):
    def test_battle(self):
        attacker = Ship()
        defender = Ship()
        battlefield = Battlefield(attacker, defender)
        result = battlefield.start()
        self.assertTrue(False)


class TestUnitMove(unittest.TestCase):
    def test_move_attacker(self):
        current_time = 0
        unit = Attacker(Ship(), current_time, Battlefield.SIZE)
        target = Battlefield.SIZE - (unit.speed() * 6)

        unit.move_to(target, current_time)
        self.assertEqual(unit.position, Battlefield.SIZE)

        current_time += 3  # 3 seconds
        unit.move_to(target, current_time)
        self.assertEqual(unit.position, Battlefield.SIZE - (unit.speed() * current_time))

        current_time += 10  # 13 seconds
        unit.move_to(target, current_time)
        self.assertEqual(unit.position, target)


class TestBattleShield(unittest.TestCase):
    def test_absorb(self):
        """absorb all damage"""
        shield = BattleShield(Shield())
        damage = Shield.defense() // 2
        damage_unabsorbed = shield.absorb(damage)
        self.assertEqual(shield._defense_left, Shield.defense()-damage)
        self.assertEqual(damage_unabsorbed, 0)

    def test_absorb1(self):
        """try to absorb more damage than shield can take"""
        shield = BattleShield(Shield())
        damage = Shield.defense() * 2
        damage_unabsorbed = shield.absorb(damage)
        self.assertEqual(shield._defense_left, 0)
        self.assertEqual(damage_unabsorbed, Shield.defense())


class TestActions(unittest.TestCase):
    def test_continuous(self):
        base_power = 10  # an arbitrary value emitted in one second, fe. power of an energy weapon

        current_time = 0
        action = ContinuousAction(current_time, base_power)

        with action.approximate(current_time) as power:
            self.assertEqual(power, 0)

        current_time += 7
        with action.approximate(current_time) as power:
            self.assertEqual(power, 7 * base_power)

        with action.approximate(current_time) as power:
            self.assertEqual(power, 0)

        current_time += 3
        with action.approximate(current_time) as power:
            self.assertEqual(power, 3 * base_power)

    def test_discrete(self):
        frequency = 5

        current_time = 0
        action = DiscreteAction(current_time, frequency)

        self.assertFalse(action.check(current_time))

        current_time += 3  # 3 seconds
        self.assertFalse(action.check(current_time))

        current_time += 3  # 6 seconds
        self.assertTrue(action.check(current_time))
        with action.process():
            pass
        self.assertFalse(action.check(current_time))

        current_time += 1  # 7 seconds
        self.assertFalse(action.check(current_time))

        current_time += 5  # 12 seconds
        self.assertTrue(action.check(current_time))
        with action.process():
            pass
        self.assertFalse(action.check(current_time))