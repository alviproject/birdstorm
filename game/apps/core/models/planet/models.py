from concurrency.fields import IntegerVersionField
from django.db import models
from game.apps.core.models.system.models import System
from game.utils.polymorph import PolymorphicBase
from jsonfield.fields import JSONField


class Planet(PolymorphicBase):
    system = models.ForeignKey(System)
    data = JSONField()
    x = models.FloatField()
    y = models.FloatField()
    version = IntegerVersionField()

    class Meta:
        app_label = 'core'


class TerrestrialPlanet(Planet):
    class Meta:
        proxy = True


class GasGiant(Planet):
    class Meta:
        proxy = True


class RedPlanet(Planet):
    class Meta:
        proxy = True


class WaterPlanet(Planet):
    class Meta:
        proxy = True


class IcePlanet(Planet):
    class Meta:
        proxy = True
