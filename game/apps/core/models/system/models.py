from django.db import models
from game.utils.polymorph import PolymorphicBase


class System(PolymorphicBase):
    x = models.FloatField()
    y = models.FloatField()

    class Meta:
        app_label = 'core'

    def planets(self):
        return self.planet_set.order_by('id')


class WhiteDwarf(System):
    class Meta: proxy = True


class BrownDwarf(System):
    class Meta: proxy = True


class BlueDwarf(System):
    class Meta: proxy = True


class BlackDwarf(System):
    class Meta: proxy = True


class RedDwarf(System):
    class Meta: proxy = True


class Dwarf(System):
    class Meta: proxy = True


class BlueSuperGiant(System):
    class Meta: proxy = True


class BlackHole(System):
    class Meta: proxy = True


class RedGiant(System):
    class Meta: proxy = True


class NeutronStar(System):
    class Meta: proxy = True


class HyperGiant(System):
    class Meta: proxy = True


class Nebula(System):
    class Meta: proxy = True


class Protostar(System):
    class Meta: proxy = True
