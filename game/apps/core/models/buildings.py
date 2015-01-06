import blinker
from concurrency.fields import IntegerVersionField
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from game.apps.core.models.planet.models import Planet
from game.utils.models import ResourceContainer
from game.utils.polymorph import PolymorphicBase
from jsonfield import JSONField
import game.apps.core.signals


class Building(PolymorphicBase):
    level = models.IntegerField(default=1)
    data = JSONField(default={})
    planet = models.ForeignKey(Planet, related_name="buildings")
    version = IntegerVersionField()
    user = models.ForeignKey(User, related_name="buildings")

    def save(self, *args, **kwargs):
        signal = blinker.signal(game.apps.core.signals.building % self.id)
        signal.send(self, building=self)
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'core'
        ordering = ('id', )


class Citadel(Building):
    class Meta:
        proxy = True

    def process_turn(self):
        warehouse = self.owner.buildings.filter(type='Warehouse')
        warehouse.add_resource("Aluminium", 10)
        warehouse.add_resource("Steel", 10)
        warehouse.save()


class Warehouse(Building, ResourceContainer):
    class Meta:
        proxy = True


class Terminal(Building):
    class Meta:
        proxy = True


class Mine(Building):
    class Meta:
        proxy = True


#TODO use Django ready()
@receiver(post_save, sender=User, dispatch_uid="create_default_buildings")
def create_default_buildings(sender, **kwargs):
    if kwargs['created']:
        Citadel.objects.create(user=kwargs['instance'], planet_id=1)  # TODO don't hard-code planet id
        Warehouse.objects.create(user=kwargs['instance'], planet_id=1)  # TODO don't hard-code planet id


def get_base(self):
    #TODO cache
    return self.buildings.get(type="Base")

User.base = property(get_base)