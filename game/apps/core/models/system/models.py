from django.db import models
from game.utils.polymorph import PolymorphicBase


class System(PolymorphicBase):
    x = models.FloatField()
    y = models.FloatField()

    class Meta:
        app_label = 'core'

    def planets(self):
        return self.planet_set.order_by('id')


class WhiteDraft(System):
    class Meta: proxy = True


class BrownDraft(System):
    class Meta: proxy = True


class BlueDraft(System):
    class Meta: proxy = True


class BlackDraft(System):
    class Meta: proxy = True


class RedDraft(System):
    class Meta: proxy = True


class Draft(System):
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
