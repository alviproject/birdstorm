from game.apps.core.models import Task
from rest_framework import serializers


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='id')
    story = serializers.Field(source='STORY.__name__')
    story_description = serializers.Field(source='STORY.DESCRIPTION')
    description = serializers.Field(source='DESCRIPTION')

    class Meta:
        model = Task
        ordering = ("id", )
