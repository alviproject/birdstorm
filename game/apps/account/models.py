from django.contrib.auth.models import User
from rest_framework import serializers


#TODO rename this class or the next one
#public user
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username')


#own account
class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'id')
