from game.utils import config
import os

import logging
import json
import django.core.handlers.wsgi
from django.conf import settings
import tornado.ioloop
import tornado.web
import tornado.wsgi
import tornado.httpserver
import django.utils.importlib
import django.contrib.auth
from django.contrib.auth.models import AnonymousUser

from sockjs.tornado import SockJSConnection
from sockjs.tornado import SockJSRouter

import game.channels
import game.tasks


logger = logging.getLogger(__name__)


class BroadcastConnection(SockJSConnection):
    #TODO csrf
    clients = set()

    def __init__(self, session):
        super().__init__(session)
        self.user = None

    def on_open(self, info):
        self.clients.add(self)

        class DjangoRequest(object):
            def __init__(self, session):
                self.session = session

        #get Django session
        engine = django.utils.importlib.import_module(django.conf.settings.SESSION_ENGINE)
        cookie_name = django.conf.settings.SESSION_COOKIE_NAME
        try:
            session_key = info.get_cookie(cookie_name).value
        except AttributeError:
            self.user = AnonymousUser()
            return
        session = engine.SessionStore(session_key)
        session = session.load()
        request = DjangoRequest(session)

        self.user = django.contrib.auth.get_user(request)

    def on_message(self, msg):
        data = json.loads(msg)
        command = data['command']
        if command == "subscribe":
            self.handle_subscribe(data)
        elif command == "unsubscribe":
            self.handle_unsubscribe(data)

    def handle_subscribe(self, params):
        logger.debug("Subscribing, params: ", params)
        channel_class, channel_name = params['channel'].split('.')
        channel = game.channels.Channel.channels[channel_class]
        channel.subscribe(self.user, self, channel_name)

    def handle_unsubscribe(self, params):
        logger.debug("unsubscribing, params: ", params)
        channel_class, channel_name = params['channel'].split('.')
        channel = game.channels.Channel.channels[channel_class]
        channel.unsubscribe(self.user, self, channel_name)

    def on_close(self):
        self.clients.remove(self)
        #channel.remove_connections(self, channel_name)
        #TODO remove all channel connections


class NoCacheStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


def main():
    wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())

    broadcast_router = SockJSRouter(BroadcastConnection, '/broadcast')

    app = tornado.web.Application(
        broadcast_router.urls +
        [
            (r"/static/(.*)", NoCacheStaticFileHandler, {"path": os.path.join(settings.PROJECT_DIR, 'static_generated')}),
            #(r"/()$", tornado.web.StaticFileHandler, {"path": os.path.join(settings.PROJECT_DIR, 'static_generated', "angular", "index.html")}),
            ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ],
        debug=config.debug,
    )

    server = tornado.httpserver.HTTPServer(app)
    server.listen(config.port, config.address)

    logger.info("listening at: http://%s:%s", config.address, config.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
