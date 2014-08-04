import game.apps.core.signals
from game.channels import receiver
from game.channels import Channel


class Sector(Channel):
    @receiver(game.apps.core.signals.ship_move)
    def ship_move(self, channel_instance):
        if channel_instance.system.id == 0:
            return
        return dict(ship=channel_instance.id, target_system=channel_instance.system.id)


class PlanetDetails(Channel):
    @receiver(game.apps.core.signals.planet_scan_progress)
    def planet_scan_progress(self, channel_instance, messages):
        return dict(messages=messages)