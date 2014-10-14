import blinker
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from game.utils.polymorph import PolymorphicBase
from jsonfield.fields import JSONField
import game.apps.core.signals


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
    mission = "UpgradeShip"

    def receive(self, sender):
        self.finish()

    def connect(self):
        blinker.signal(game.apps.core.signals.planet_scan % self.user_id).connect(self.receive)

    class Meta:
        proxy = True


class Panels(Task):
    mission = "LearnTheInterface"

    def receive(self, sender):
        self.finish()

    def connect(self):
        blinker.signal(game.apps.core.signals.planet_scan % self.user_id).connect(self.receive)

    def action(self, _type):
        #TODO this probably should utilize state pattern, although it's yet to be decided how to refactor this,
        # once there are some more complicated tasks
        if self.state == "started" and _type == 'acknowledge':
            self.state = "click_any_system"
        elif self.state == "click_any_system" and _type == 'planet':
            self.state = "planet_not_star"
        elif self.state == "click_any_system" and _type == 'star':
            self.state = "star_system"
        elif self.state == "star_system" and _type == 'acknowledge':
            self.state = "left_panels"
        elif self.state == "planet_not_star" and _type == 'acknowledge':
            self.state = "left_panels"
        elif self.state == "left_panels" and _type == 'acknowledge':
            self.state = "close_details"
        elif self.state == "close_details" and _type == 'acknowledge':
            self.state = "map"
        elif self.state == "map" and _type == 'acknowledge':
            self.state = "finish"
        else:
            raise RuntimeError("Wrong state or type: %s, %s" % (self.state, _type))
        self.save()

    class Meta:
        proxy = True


def create_task(sender, instance, created, *args, **kwargs):
    if created:
        Panels.objects.create(user=instance)


post_save.connect(create_task, sender=User, dispatch_uid="create_task")