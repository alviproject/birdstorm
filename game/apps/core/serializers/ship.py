from rest_framework import serializers
from game.apps.core.models import Ship


class ShipSerializer(serializers.HyperlinkedModelSerializer):
    planet_id = serializers.CharField(source='planet_id', read_only=True)
    id = serializers.IntegerField(source='id', read_only=True)
    components = serializers.SerializerMethodField('get_components')
    system_id = serializers.SerializerMethodField('get_system_id')
    owner_username = serializers.SerializerMethodField('get_owner_username')
    speed = serializers.Field('speed')

    #TODO could be calculated on client side
    def get_system_id(self, obj):
        return obj.planet.system_id

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

    def get_owner_username(self, obj):
        return obj.owner.username

    class Meta:
        model = Ship
        fields = ['id', 'url', 'type', 'planet_id', 'owner', 'planet', 'system_id', 'components', 'owner_username']


class OwnShipSerializer(ShipSerializer):
    id = serializers.IntegerField(source='id', read_only=True)


class OwnShipDetailsSerializer(OwnShipSerializer):
    planet_id = serializers.CharField(source='planet_id', read_only=True)
    resources = serializers.Field(source='resources')

    class Meta:
        model = Ship
        fields = ShipSerializer.Meta.fields + ['locked', 'resources']
