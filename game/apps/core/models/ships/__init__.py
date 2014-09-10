from contextlib import contextmanager

import blinker
from django.contrib.auth.models import User
from game.apps.core.models.components.drills import Drill
from game.apps.core.models.components.engines import Engine
from game.apps.core.models.components.scanners import Scanner
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

    @property
    def engine(self):
        #TODO cache
        return Engine.create(self.data.get('components', {}).get('engine', {"mark": 0}))

    @property
    def drill(self):
        #TODO cache
        return Drill.create(self.data.get('components', {}).get('drill', {}))

    @property
    def scanner(self):
        #TODO cache
        return Scanner.create(self.data.get('components', {}).get('scanner', {}))

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
    engine = serializers.SerializerMethodField('get_engine')
    drill = serializers.SerializerMethodField('get_drill')
    scanner = serializers.SerializerMethodField('get_scanner')
    speed = serializers.Field('speed')

    def get_engine(self, obj):
        return {
            "mark": obj.engine.mark,
            "type": obj.engine.type,
            "output": obj.engine.output,
            "range": obj.engine.range,
        }

    def get_drill(self, obj):
        return {
            "mark": obj.drill.mark,
            "type": obj.drill.type,
            "deepness": obj.drill.deepness,
            "speed": obj.drill.speed,
        }

    def get_scanner(self, obj):
        return {
            "mark": obj.scanner.mark,
            "type": obj.scanner.type,
            "deepness": obj.scanner.deepness,
        }

    class Meta:
        model = Ship
        fields = ['id', 'url', 'type', 'system_id', 'owner', 'system', 'engine', 'speed', 'drill', 'scanner']


class OwnShipSerializer(ShipSerializer):
    id = serializers.IntegerField(source='id', read_only=True)


class OwnShipDetailsSerializer(OwnShipSerializer):
    system_id = serializers.CharField(source='system_id', read_only=True)
    resources = serializers.Field(source='resources')

    class Meta:
        model = Ship
        fields = ShipSerializer.Meta.fields + ['locked', 'resources']
