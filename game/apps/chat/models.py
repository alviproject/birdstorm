from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers


class Message(models.Model):
    author = models.ForeignKey(User)
    text = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.RelatedField(many=False)

    class Meta:
        model = Message
