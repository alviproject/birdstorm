from game.apps.core.models import Task
from rest_framework import serializers


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    mission = serializers.ReadOnlyField()
    details = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = ("id", "mission", "url", "type", "details", "state")
