from rest_framework import serializers
from game.apps.core.models.planet.models import Planet


class PlanetSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Planet
        fields = ['id', 'url', 'type', 'system']


class PlanetDetailsSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)
    scan_results = serializers.SerializerMethodField('get_scan_results')

    def get_scan_results(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated():
            return []
        return user.profile.get_scan_results(obj.id)

    class Meta:
        model = Planet
        fields = ['id', 'url', 'type', 'system', 'scan_results']
