from contextlib import contextmanager
import blinker
from django.contrib.auth.models import User
import game.apps.core.signals
from game.apps.core.models.armors import Armor
from game.apps.core.models.shields import Shield
from game.apps.core.models.weapons import ElectronBeam
import game.apps.core.signals
from game.utils.models import ResourceContainer
from game.utils.polymorph import PolymorphicBase
from django.db import models
from jsonfield.fields import JSONField
from rest_framework import serializers


class Ship(PolymorphicBase, ResourceContainer):
    owner = models.ForeignKey(User)
    system = models.ForeignKey('System')  # TODO change it to planet
    data = JSONField(default={})  # TODO schema validation
    locked = models.BooleanField(default=False)

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
        return 2

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        ship_signal = blinker.signal(game.apps.core.signals.own_ship_data % self.id)
        ship_signal.send(None, ship=OwnShipDetailsSerializer(self).data)

    class Meta:
        app_label = 'core'


class Raven(Ship):
    class Meta:
        proxy = True


class ShipSerializer(serializers.HyperlinkedModelSerializer):
    system_id = serializers.CharField(source='system_id', read_only=True)
    id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Ship
        fields = ['id', 'url', 'type', 'system_id', 'owner', 'system']


class OwnShipSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Ship
        fields = ['id', 'url', 'type']


class OwnShipDetailsSerializer(OwnShipSerializer):
    system_id = serializers.CharField(source='system_id', read_only=True)
    resources = serializers.Field(source='resources')

    class Meta:
        model = Ship
        fields = ['id', 'url', 'type', 'owner', 'system', 'locked', 'resources', 'system_id']
