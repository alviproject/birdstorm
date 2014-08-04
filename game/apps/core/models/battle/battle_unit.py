from math import copysign
import contextlib

import abc
from game.apps.core.models.battle.base import BattleOver


class Action:
    """
    abstract class that represents action that may be performed during the battle
    action depends on time that passes during the battle
    see derived classes for the details
    """
    def __init__(self, current_time):
        self._time = current_time


class DiscreteAction(Action):
    """action that may happen in discrete intervals"""
    def __init__(self, current_time, frequency):
        super().__init__(current_time)
        self._frequency = frequency
        self._last_check = 0

    @contextlib.contextmanager
    def process(self):
        """
        may be safely called under following conditions:
        1. last call to check returned True
        2. time counter has not changed since last call to check
        """
        yield
        self._time = self._last_check

    def check(self, current_time):
        self._last_check = current_time
        return current_time - self._time > self._frequency


class ContinuousAction(Action):
    """continuous action, like movement of the ship"""
    def __init__(self, current_time, base_value):
        """
        base_value may be an arbitrary value per one second
        fe. power of a energy weapon (assuming that this weapon shoots continuously)
        or distance that ship can cover in one second
        """
        super().__init__(current_time)
        self._base_value = base_value

    @contextlib.contextmanager
    def approximate(self, current_time):
        """
        return value of a power that was emitted since last time
        """
        yield (current_time - self._time) * self._base_value
        self._time = current_time


class BattleWeapon:
    """
    decorator for any kind of weapon that is used in particular battle
    delegates most of the logic to the decorated object, plus adds some methods specific for the battle
    """
    def __init__(self, weapon, current_time):
        self._weapon = weapon
        self._action = DiscreteAction(current_time, self._weapon.frequency())

    def process(self, battlefield, battle_unit):
        if not self._action.check(battlefield.time()):
            return
        enemy = battle_unit.enemy(battlefield)
        if self._weapon.range() < battle_unit.distance_to(enemy.position):
            return  # too far to shoot
        with self._action.process():
            enemy.absorb(self)

    def damage(self):
        return self._weapon.damage()


class BattleShield:
    """
    decorator for any kind of shield that is used in particular battle
    delegates most of the logic to the decorated object, plus adds some methods specific for the battle
    """
    def __init__(self, shield):
        self._shield = shield
        #shields regain the whole defense after each battle
        self._defense_left = shield.defense()

    def absorb(self, damage):
        """absorb as much damage as possible, return amount of damage that was not absorbed"""
        taken_damage = min(self._defense_left, damage)
        self._defense_left -= taken_damage
        return damage - taken_damage


class BattleArmor:
    """
    decorator for any kind of armor that is used in particular battle
    delegates most of the logic to the decorated object, plus adds some methods specific for the battle
    """
    def __init__(self, armor):
        self._armor = armor

    def absorb(self, damage):
        """absorb as much damage as possible, return amount of damage that was not absorbed"""
        taken_damage = min(self._armor.defense_left, damage)
        self._armor.defense_left -= taken_damage
        return damage - taken_damage


class BattleUnit:
    """
    decorator for ships, rockets, etc
    delegates most of the logic to the decorated object, plus adds some methods specific for the battle
    """
    def __init__(self, unit, current_time, position):
        self.position = position
        self._unit = unit
        self.weapons = [BattleWeapon(w, current_time) for w in unit.weapons]
        self.shields = [BattleShield(s) for s in unit.shields]
        self.armors = [BattleArmor(a) for a in unit.armors]
        self._movement_action = ContinuousAction(current_time, self.speed())

    def speed(self):
        return self._unit.speed()

    def effective_range(self):
        return self._unit.effective_range()

    def distance_to(self, position):
        return abs(self.position-position)

    def approach(self, battlefield):
        enemy = self.enemy(battlefield)
        distance = self.distance_to(enemy.position)
        if distance > self.effective_range():
            self.move_to(enemy.position, battlefield.time())

    def move_to(self, position, current_time):
        """move as fast as unit can in the direction specified by coordinate x"""
        distance = position - self.position
        movement_action = self._movement_action
        with movement_action.approximate(current_time) as max_distance:
            self.position += int(copysign(min(abs(distance), max_distance), distance))

    def process_weapons(self, battlefield):
        for weapon in self.weapons:
            weapon.process(battlefield, self)

    def process(self, battlefield):
        self.process_weapons(battlefield)
        self.approach(battlefield)

    @abc.abstractmethod
    def enemy(self, battlefield):
        raise NotImplementedError

    def absorb(self, weapon):
        damage = weapon.damage()
        for shield in self.shields:
            damage = shield.absorb(damage)
            if damage == 0:
                return  # shields absorbed all the damage

        #there is still some damage to absorb
        for armor in self.armors:
            damage = armor.absorb(damage)
            if damage == 0:
                return  # armors absorbed all remaining damage

        #ship was not able to absorb the whole damage, the battle is over
        raise BattleOver(loser=self)


class Attacker(BattleUnit):
    def enemy(self, battlefield):
        return battlefield.defender


class Defender(BattleUnit):
    def enemy(self, battlefield):
        return battlefield.defender
