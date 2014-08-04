from game.apps.core.models.planet.serializers import PlanetSerializer
from game.apps.core.models.system.models import System
from rest_framework import serializers


class SystemSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = System


class SystemDetailsSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)
    planets = PlanetSerializer(many=True)

    class Meta:
        model = System
