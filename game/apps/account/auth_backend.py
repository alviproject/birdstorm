from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class AuthBackend(ModelBackend):
    """Log in to Django with User object"""
    def authenticate(self, user=None, password=None, **kwargs):
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None