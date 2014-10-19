import logging
from game.apps.core.models.tasks import Task
from game.apps.core.serializers.ship import OwnShipSerializer
from game.apps.core.serializers.tasks import TaskSerializer
import game.apps.core.signals
from game.channels import receiver
from game.channels import Channel
from game.apps.core.models.ships import Ship

logger = logging.getLogger(__name__)


class Sector(Channel):
    @receiver(game.apps.core.signals.ship_move)
    def ship_move(self, ship, time):
        return dict(ship=ship.id, target_planet=ship.planet.id, time=time)


class PlanetDetails(Channel):
    @receiver(game.apps.core.signals.planet_details)
    def planet_scan_progress(self, channel_instance, **kwargs):
        return dict(**kwargs)


#TODO consider moving this to account
class Messages(Channel):
    @receiver(game.apps.core.signals.messages)
    def messages(self, channel_instance, **kwargs):
        return dict(**kwargs)


class OwnShip(Channel):
    @receiver(game.apps.core.signals.own_ship_data)
    def own_ship_data(self, channel_instance, ship):
        return dict(ship=ship)

    @classmethod
    def has_permissions(cls, user, name):
        ship = Ship.objects.get(pk=name)
        return ship.owner == user


class OwnShips(Channel):
    @receiver(game.apps.core.signals.own_ship_list)
    def own_ship_list(self, channel_instance, new_ship_id):
        ships = Ship.objects.filter(owner=self.name)
        result = dict(
            ships=OwnShipSerializer(ships, many=True, context={'request': 0}).data,
            current_ship_id=new_ship_id,
        )
        return result

    @classmethod
    def has_permissions(cls, user, name):
        return user.id == int(name)


class NewShip(Channel):
    @receiver(game.apps.core.signals.new_ship)
    def new_ship(self, channel_instance, ship):
        result = dict(
            ship=OwnShipSerializer(ship, context={'request': 0}).data,
        )
        return result


#TODO consider moving this to account
class Account(Channel):
    @receiver(game.apps.core.signals.account_data)
    def account_data(self, channel_instance, data):
        return dict(data=data)

    @classmethod
    def has_permissions(cls, user, name):
        return user.id == int(name)


class BuildingUser(Channel):
    """broadcasts building changes custom for particular user"""
    @receiver(game.apps.core.signals.building_user)
    def building_user(self, channel_instance, **kwargs):
        return dict(**kwargs)

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
            updated=kwargs['task_id'],
        )

    #FIXME permissions