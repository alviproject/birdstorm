import blinker
from rest_framework.decorators import api_view
from game.apps.chat import models
import game.apps.chat.signals
import logging
from rest_framework import viewsets, generics
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class Messages(viewsets.ReadOnlyModelViewSet):
    model = models.Message
    serializer_class = models.MessageSerializer
    paginate_by = 3
    queryset = models.Message.objects.order_by('-created')

    def create(self, request, *args, **kwargs):
        text = request.DATA['text']
        author = request.user
        models.Message.objects.create(text=text, author=author)
        signal_name = game.apps.chat.signals.message
        blinker.signal(signal_name % "general_room").send('general_room', text=text, author=author)
        return Response()
