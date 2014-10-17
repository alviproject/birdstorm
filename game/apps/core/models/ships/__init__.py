from contextlib import contextmanager

import blinker
from django.contrib.auth.models import User
from game.apps.core.models.components import create_kind
import game.apps.core.signals
from game.apps.core.models.armors import Armor
from game.apps.core.models.shields import Shield
from game.apps.core.models.weapons import ElectronBeam
import game.apps.core.signals
from game.utils.models import ResourceContainer
from game.utils.polymorph import PolymorphicBase
from django.db import models
from jsonfield.fields import JSONField
from concurrency.fields import IntegerVersionField


class Ship(PolymorphicBase, ResourceContainer):
    owner = models.ForeignKey(User)
    system = models.ForeignKey('System')  # TODO change it to planet
    data = JSONField(default={})  # TODO schema validation
    locked = models.BooleanField(default=False)
    version = IntegerVersionField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weapons = [
            ElectronBeam(),
        ]
        self.shields = [
            Shield(),
        ]
        self.armors = [
            Armor(),
        ]

        self.components = {
            'Drill': create_kind('Drill').create(self.data.get('components', {}).get('Drill', {})),
            'Engine': create_kind('Engine').create(self.data.get('components', {}).get('Engine', {})),
            'Scanner': create_kind('Scanner').create(self.data.get('components', {}).get('Scanner', {})),
        }

    @property
    def engine(self):
        return self.components["Engine"]

    @property
    def drill(self):
        return self.components["Drill"]

    @property
    def scanner(self):
        return self.components["Scanner"]

    @contextmanager
    def lock(self):
        if self.locked:
            raise RuntimeError("object %s, %d already locked" % (self.__class__.__name__, self.id))
        self.locked = True
        self.save()
        try:
            yield
        finally:
            self.locked = False
            self.save()

    def effective_range(self):
        return min(w.range() for w in self.weapons)

    @staticmethod
    def speed():
        return 2  # TODO

    def save(self, *args, **kwargs):
        created = self.pk is None

        self.data = {
            'components': {name: component.serialize() for name, component in self.components.items()}
        }
        ResourceContainer.save(self, *args, **kwargs)
        super().save(*args, **kwargs)
        ship_signal = blinker.signal(game.apps.core.signals.own_ship_data % self.id)

        #TODO refactor
        from game.apps.core.serializers.ship import OwnShipDetailsSerializer
        ship_signal.send(None, ship=OwnShipDetailsSerializer(self, context={'request': 0}).data)

        if created:
            signal = blinker.signal(game.apps.core.signals.own_ship_list % self.owner.id)
            signal.send(None, new_ship_id=self.id)

            signal = blinker.signal(game.apps.core.signals.new_ship % 'main')
            signal.send(None, ship=self)

    class Meta:
        app_label = 'core'


class Raven(Ship):
    class Meta:
        proxy = True


class Swallow(Ship):
    class Meta:
        proxy = True


class Owl(Ship):
    class Meta:
        proxy = True

