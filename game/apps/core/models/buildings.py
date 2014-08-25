from django.db import models
from game.apps.core.models.planet.models import Planet
from game.utils.polymorph import PolymorphicBase
from jsonfield import JSONField
from rest_framework import serializers


class Building(PolymorphicBase):
    level = models.IntegerField(default=1)
    data = JSONField()
    planet = models.ForeignKey(Planet, related_name="buildings")

    class Meta:
        app_label = 'core'


class Port(Building):
    OFFER_FACTOR = 1.5

    @property
    def prices(self):
        base_prices = self.data.get('prices') or {}
        print(base_prices)
        return {(t, (int(p/Port.OFFER_FACTOR), int(p*Port.OFFER_FACTOR))) for (t, p) in base_prices.items()}

    class Meta:
        proxy = True


class Factory(Building):
    class Meta:
        proxy = True
        

class Mine(Building):
    class Meta:
        proxy = True


class BuildingBaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Building
        exclude = ['data']


class PortSerializer(BuildingBaseSerializer):
    prices = serializers.Field(source='prices')


class BuildingSerializer(serializers.HyperlinkedModelSerializer):
    def to_native(self, obj):
        if obj.type == "Port":  # TODO may be done automatically
            return PortSerializer(obj).to_native(obj)
        return super().to_native(obj)

    class Meta(BuildingBaseSerializer.Meta):
        pass