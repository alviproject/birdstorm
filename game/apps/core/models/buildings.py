from django.db import models
from game.apps.core.models.planet.models import Planet
from game.utils.models import ResourceContainer
from game.utils.polymorph import PolymorphicBase
from jsonfield import JSONField
from rest_framework import serializers


class Building(PolymorphicBase):
    level = models.IntegerField(default=1)
    data = JSONField()
    planet = models.ForeignKey(Planet, related_name="buildings")

    class Meta:
        app_label = 'core'


class Port(Building, ResourceContainer):
    OFFER_FACTOR = 1.5

    @property
    def prices(self):
        base_prices = self.data.get('prices') or {}
        result = dict()
        for type, price in base_prices.items():
            result[type] = dict(
                sale_price=int(price*Port.OFFER_FACTOR),
                purchase_price=int(price/Port.OFFER_FACTOR),
                available=self.resources.get(type, 0),
            )
        return result

    class Meta:
        proxy = True


class Factory(Building):
    class Meta:
        proxy = True


class Mine(Building):
    class Meta:
        proxy = True


class Shipyard(Building):
    class Meta:
        proxy = True


class BuildingBaseSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)

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