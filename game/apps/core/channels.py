import game.apps.core.signals
from game.channels import receiver
from game.channels import Channel


class Sector(Channel):
    @receiver(game.apps.core.signals.ship_move)
    def ship_move(self, channel_instance):
        return dict(ship=channel_instance.id, target_system=channel_instance.system.id)


class PlanetDetails(Channel):
    @receiver(game.apps.core.signals.planet_scan_progress)
    def planet_scan_progress(self, channel_instance, messages):
        return dict(messages=messages)


class Profile(Channel):
    @receiver(game.apps.core.signals.own_ships_data)
    def own_ships_data(self, channel_instance, ship):
        return dict(ship=ship)