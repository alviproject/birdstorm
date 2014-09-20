from game.apps.core.models.buildings import Building, Provider
from rest_framework import serializers


class BuildingBaseSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Building
        exclude = ['data']


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


class BuildingSerializer(serializers.HyperlinkedModelSerializer):
    def to_native(self, obj):
        #TODO use isinstance
        if obj.type == "Port":
            return PortSerializer(obj, context=self.context).to_native(obj)
        if isinstance(obj, Provider):
            return ProviderSerializer(obj, context=self.context).to_native(obj)
        if obj.type == "Warehouse":
            return WarehouseSerializer(obj, context=self.context).to_native(obj)
        return super().to_native(obj)

    class Meta(BuildingBaseSerializer.Meta):
        pass
