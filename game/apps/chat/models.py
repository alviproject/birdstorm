from concurrency.fields import IntegerVersionField
from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers


class Message(models.Model):
    author = models.ForeignKey(User)
    text = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    version = IntegerVersionField()


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.RelatedField(read_only=True)

    class Meta:
        model = Message
