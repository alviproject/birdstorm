import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game.settings")
from game.utils import config

import logging
import json
import django.core.handlers.wsgi
from django.conf import settings
import tornado.ioloop
import tornado.web
import tornado.wsgi
import tornado.httpserver

from sockjs.tornado import SockJSConnection
from sockjs.tornado import SockJSRouter

import game.channels
import game.tasks


logger = logging.getLogger(__name__)


class BroadcastConnection(SockJSConnection):
    clients = set()

    def on_open(self, info):
        self.clients.add(self)

    def on_message(self, msg):
        data = json.loads(msg)
        command = data['command']
        if command == "connect":
            self.handle_connect(data)

    def handle_connect(self, params):
        channel_class, channel_name = params['channel'].split('.')
        channel = game.channels.Channel.channels[channel_class]
        user = None  # TODO
        channel.subscribe(user, self, channel_name)

    def on_close(self):
        self.clients.remove(self)
        #TODO remove all channel connections


def main():
    print(settings.PROJECT_DIR)
    wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())

    broadcast_router = SockJSRouter(BroadcastConnection, '/broadcast')

    app = tornado.web.Application(
        broadcast_router.urls +
        [
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(settings.PROJECT_DIR, 'static_generated')}),
            (r"/()$", tornado.web.StaticFileHandler, {"path": os.path.join(settings.PROJECT_DIR, 'static_generated', "angular", "index.html")}),
            ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ],
        debug=True,  # TODO get this from settings
    )

    server = tornado.httpserver.HTTPServer(app)
    server.listen(config.port, config.address)

    logger.info("listening at: http://%s:%s", config.address, config.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
