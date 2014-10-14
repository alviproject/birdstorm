from game.apps.core.models import Task
from rest_framework import serializers


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='id')
    mission = serializers.Field(source='mission')

    class Meta:
        model = Task
        ordering = ("id", )
