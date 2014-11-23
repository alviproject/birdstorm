import logging
from game.apps.core.models.tasks import Task
from game.apps.core.serializers.buildings import BuildingSerializer
from game.apps.core.serializers.tasks import TaskSerializer
import game.apps.core.signals
from game.channels import receiver
from game.channels import Channel

logger = logging.getLogger(__name__)


class Sector(Channel):
    pass


class Planet(Channel):
    @receiver(game.apps.core.signals.planet)
    def planet_scan_progress(self, channel_instance, **kwargs):
        return dict(**kwargs)


class Messages(Channel):
    @receiver(game.apps.core.signals.messages)
    def messages(self, channel_instance, **kwargs):
        return dict(**kwargs)


#TODO consider moving this to account
class Account(Channel):
    @receiver(game.apps.core.signals.account_data)
    def account_data(self, channel_instance, data):
        return dict(data=data)

    @classmethod
    def has_permissions(cls, user, name):
        return user.id == int(name)


class Building(Channel):
    """broadcasts building changes"""
    @receiver(game.apps.core.signals.building)
    def building(self, channel_instance, building):
        return dict(
            building=BuildingSerializer(building, context=dict(request={})).data
        )

    #FIXME permissions


class Tasks(Channel):
    @classmethod
    def subscribe(cls, user, connection, name):
        instance = super().subscribe(user, connection, name)
        instance.init_tasks()

    def tasks(self):
        #TODO this should utilize same functionality as implemented in views
        # same for other Channels
        return Task.objects.filter(user=self.name, archived=False)

    def init_tasks(self):
        self.receivers = []

        #FIXME disconnect (or possibly just delete tasks after unsubscribe)
        for task in self.tasks():
            self.receivers.append(task.connect())

    @receiver(game.apps.core.signals.task_updated)
    def task_updated(self, channel_instance, **kwargs):
        self.init_tasks()
        return dict(
            tasks=TaskSerializer(self.tasks(), many=True, context={'request': 0}).data,
            updated_task=kwargs['task_id'],
            archived=kwargs['archived'],
            state=kwargs['state'],
            type=kwargs['type'],
        )

    #FIXME permissions