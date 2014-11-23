from game.apps.core.models.buildings import Building, Provider
from rest_framework import serializers


class BuildingBaseSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Building
        exclude = ['data']
        order = ('id', )


class PortSerializer(BuildingBaseSerializer):
    prices = serializers.Field(source='prices')


class ProviderSerializer(BuildingBaseSerializer):
    processes = serializers.Field(source='processes')


#class WorkshopSerializer(BuildingBaseSerializer):
#    processes = serializers.SerializerMethodField('get_processes')
#
#    def get_processes(self, obj):
#        user = self.context['request'].user
#        if not user.is_authenticated():
#            return {}
#        return user.profile.warehouse_resources(obj.id)


class WarehouseSerializer(BuildingBaseSerializer):
    resources = serializers.SerializerMethodField('get_resources')

    def get_resources(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated():
            return {}
        return obj.Container(user).resources


class CitadelSerializer(BuildingBaseSerializer):
    resources = serializers.Field('resources')


class BuildingSerializer(serializers.HyperlinkedModelSerializer):
    def to_native(self, obj):
        #TODO use isinstance
        if obj.type == "Port":
            serializer = PortSerializer
        elif isinstance(obj, Provider):
            serializer = ProviderSerializer
        elif obj.type == "Warehouse":
            serializer = WarehouseSerializer
        elif obj.type == "Citadel":
            serializer = CitadelSerializer
        else:
            serializer = BuildingBaseSerializer

        return serializer(obj, context=self.context).to_native(obj)

    class Meta(BuildingBaseSerializer.Meta):
        pass
