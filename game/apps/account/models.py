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
    credits = serializers.SerializerMethodField('get_credits')
    is_authenticated = serializers.Field('is_authenticated')

    def get_credits(self, obj):
        if not obj.is_authenticated():
            return
        return obj.profile.credits

    class Meta:
        model = User
        fields = ('url', 'username', 'id', 'credits', 'is_authenticated', 'email')
