from django.contrib.auth.models import User
from rest_framework import serializers


#TODO rename this class or the next one
#public user
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username')


#own account
#TODO move this class to core.profile
class AccountSerializer(serializers.HyperlinkedModelSerializer):
    email = serializers.SerializerMethodField('get_email')
    is_authenticated = serializers.Field('is_authenticated')

    def get_email(self, obj):
        if not obj.is_authenticated():
            return ""
        return obj.email

    class Meta:
        model = User
        fields = ('url', 'username', 'id', 'is_authenticated', 'email')
