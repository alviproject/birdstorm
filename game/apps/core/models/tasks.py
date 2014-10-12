from enum import Enum
import blinker
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from game.utils.polymorph import PolymorphicBase
from jsonfield.fields import JSONField
import game.apps.core.signals


class UpgradeShip:
    DESCRIPTION = "Sample description"


class Task(PolymorphicBase):
    user = models.ForeignKey(User)
    data = JSONField(default={})  # TODO schema validation
    state = models.CharField(max_length=256, default="started")
    archived = models.BooleanField(default=False)

    def finish(self):
        self.state = "finished"
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        signal = blinker.signal(game.apps.core.signals.task_updated % self.user_id)
        signal.send(None, task_id=self.id)


class FirstScan(Task):
    STORY = UpgradeShip
    DESCRIPTION = "Task description"

    def receive(self, sender):
        self.finish()

    def connect(self):
        blinker.signal(game.apps.core.signals.planet_scan % self.user_id).connect(self.receive)

    class Meta:
        proxy = True


def create_task(sender, instance, created, *args, **kwargs):
    if created:
        FirstScan.objects.create(user=instance)


post_save.connect(create_task, sender=User, dispatch_uid="create_task")