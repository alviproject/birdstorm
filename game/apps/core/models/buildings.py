from django.db import models
from game.utils.polymorph import PolymorphicBase
from jsonfield import JSONField


class Building(PolymorphicBase):
    level = models.IntegerField(default=1)
    data = JSONField()

    class Meta:
        app_label = 'core'


class Factory(Building):
    class Meta:
        abstract = True
        

class Mine(Building):
    class Meta:
        abstract = True