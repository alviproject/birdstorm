from game.apps.core.serializers.buildings import BuildingSerializer
from rest_framework import serializers
from game.apps.core.models.planet.models import Planet


class PlanetSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    system_id = serializers.ReadOnlyField()

    class Meta:
        model = Planet
        fields = ['id', 'url', 'type', 'system', 'system_id', 'x', 'y']
        ordering = ('id', )


class PlanetDetailsSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    buildings = serializers.SerializerMethodField()

    def get_buildings(self, obj):
        request = self.context['request']
        return BuildingSerializer(request.user.buildings.filter(planet=obj),
                                  context={'request': request}, many=True).data

    class Meta:
        model = Planet
        fields = ['id', 'url', 'type', 'system', 'buildings']
