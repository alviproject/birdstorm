import logging
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from game.apps.core.models.ships import Raven
from game.tasks.base import Task
from game.tasks.base import register


logger = logging.getLogger(__name__)


#TODO remove whole module
@register
class Register(Task):
    @classmethod
    def register(cls):
        post_save.connect(cls.create_ship, sender=User, dispatch_uid="123")  # TODO change dispach_uid

    @classmethod
    def create_ship(cls, created, **kwargs):
        if not created:
            return
        user = kwargs['instance']
        Raven.objects.create(owner=user)  # TODO don't hardcode data here