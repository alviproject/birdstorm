import game.apps.chat.signals
from game.channels import Channel, receiver


class Chat(Channel):
    @receiver(game.apps.chat.signals.message)
    def message(self, channel_instance, text, author):
        return dict(text=text, author=author.username)
