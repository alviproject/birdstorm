from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from game.utils.polymorph import PolymorphicBase
from jsonfield.fields import JSONField


class Task(PolymorphicBase):
    user = models.ForeignKey(User)
    data = JSONField(default={})  # TODO schema validation


class FirstScan(Task):
    STORY = "UpgradeShip"

    class Meta:
        proxy = True


def create_task(sender, instance, created, **kwargs):
    if created:
        FirstScan.objects.create(user=instance)


post_save.connect(create_task, sender=User, dispatch_uid="create_task")