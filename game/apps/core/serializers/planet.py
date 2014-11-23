from game.apps.core.serializers.buildings import BuildingSerializer
from rest_framework import serializers
from game.apps.core.models.planet.models import Planet


class PlanetSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)
    system_id = serializers.Field(source='system_id')

    class Meta:
        model = Planet
        fields = ['id', 'url', 'type', 'system', 'system_id', 'x', 'y']
        ordering = ('id', )


class PlanetDetailsSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)
    buildings = BuildingSerializer(many=True)

    class Meta:
        model = Planet
        fields = ['id', 'url', 'type', 'system', 'buildings']
