from game.apps.core.models.buildings import Building
from rest_framework import serializers


class BuildingBaseSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Building
        exclude = ['data']
        order = ('id', )


class CitadelSerializer(BuildingBaseSerializer):
    resources = serializers.Field('resources')


class BuildingSerializer(serializers.HyperlinkedModelSerializer):
    def to_native(self, obj):
        #TODO use isinstance
        if obj.type == "Citadel":
            serializer = CitadelSerializer
        else:
            serializer = BuildingBaseSerializer

        return serializer(obj, context=self.context).to_native(obj)

    class Meta(BuildingBaseSerializer.Meta):
        pass
