from game.apps.core.serializers.planet import PlanetSerializer
from game.apps.core.models.system.models import System
from rest_framework import serializers


#TODO both looks the same at the moment
class SystemSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)
    planets = PlanetSerializer(many=True)

    class Meta:
        model = System


class SystemDetailsSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)
    planets = PlanetSerializer(many=True)

    class Meta:
        model = System
