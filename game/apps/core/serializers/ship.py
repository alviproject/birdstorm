from rest_framework import serializers
from game.apps.core.models import Ship


class ShipSerializer(serializers.HyperlinkedModelSerializer):
    system_id = serializers.CharField(source='system_id', read_only=True)
    id = serializers.IntegerField(source='id', read_only=True)
    components = serializers.SerializerMethodField('get_components')
    speed = serializers.Field('speed')

    def get_components(self, obj):
        return {
            "Engine": {
                "mark": obj.engine.mark,
                "type": obj.engine.type,
                "output": obj.engine.output,
                "range": obj.engine.range,
                },
            "Drill": {
                "mark": obj.drill.mark,
                "type": obj.drill.type,
                "deepness": obj.drill.deepness,
                "speed": obj.drill.speed,
                },
            "Scanner": {
                "mark": obj.scanner.mark,
                "type": obj.scanner.type,
                "deepness": obj.scanner.deepness,
                }
        }

    class Meta:
        model = Ship
        fields = ['id', 'url', 'type', 'system_id', 'owner', 'system', 'components']


class OwnShipSerializer(ShipSerializer):
    id = serializers.IntegerField(source='id', read_only=True)


class OwnShipDetailsSerializer(OwnShipSerializer):
    system_id = serializers.CharField(source='system_id', read_only=True)
    resources = serializers.Field(source='resources')

    class Meta:
        model = Ship
        fields = ShipSerializer.Meta.fields + ['locked', 'resources']
