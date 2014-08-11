import blinker
from django.contrib.auth.models import User
import game.apps.core.signals
from game.apps.core.models.armors import Armor
from game.apps.core.models.shields import Shield
from game.apps.core.models.weapons import ElectronBeam
import game.apps.core.signals
from game.utils.polymorph import PolymorphicBase
from django.db import models
from jsonfield.fields import JSONField
from rest_framework import serializers


class Ship(PolymorphicBase):
    owner = models.ForeignKey(User)
    system = models.ForeignKey('System')  # TODO change it to planet
    data = JSONField()

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

    def effective_range(self):
        return min(w.range() for w in self.weapons)

    @staticmethod
    def speed():
        return 2

    def move(self, system):
        self.system = system
        self.save()
        signal_name = game.apps.core.signals.ship_move
        blinker.signal(signal_name % 'main').send(self)

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


class OwnShipSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Ship
        fields = ['id', 'url', 'type']


class OwnShipDetailsSerializer(OwnShipSerializer):
    class Meta:
        model = Ship
