import logging
import game.apps.core.signals
from game.channels import receiver
from game.channels import Channel
from game.apps.core.models.ships import OwnShipDetailsSerializer, Ship

logger = logging.getLogger(__name__)


class Sector(Channel):
    @receiver(game.apps.core.signals.ship_move)
    def ship_move(self, ship, time):
        return dict(ship=ship.id, target_system=ship.system.id, time=time)


class PlanetDetails(Channel):
    @receiver(game.apps.core.signals.planet_scan_progress)
    def planet_scan_progress(self, channel_instance, message):
        return dict(message=message)


class OwnShip(Channel):
    @receiver(game.apps.core.signals.own_ship_data)
    def own_ships_data(self, channel_instance, ship):
        return dict(ship=OwnShipDetailsSerializer(ship).data)

    @classmethod
    def has_permissions(cls, user, name):
        ship = Ship.objects.get(pk=name)
        return ship.owner == user