from game.apps.core.models import Task
from rest_framework import serializers


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='id')
    mission = serializers.Field(source='mission')
    details = serializers.Field(source='details')

    class Meta:
        model = Task
        fields = ("id", "mission", "url", "type", "details", "state")
