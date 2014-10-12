import abc
from functools import wraps
import logging
from django.conf import settings
import importlib
import blinker


logger = logging.getLogger(__name__)


class ChannelMeta(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name == 'Channel':
            #this method shall be called only for subclasses of Channel
            return
        cls.register()
        for name, attr in attrs.items():
            if hasattr(attr, '_signal_name'):
                cls.add_receiver(attr._signal_name, attr)


class Channel(metaclass=ChannelMeta):
    """this class aggregates multiple signals and broadcasts messages emmited by these signals"""
    channels = {}

    def __init__(self, name):
        self.connections = set()
        self.name = name
        self.__class__.instances[name] = self

        # just for keeping reference to make_connector, passing weak=False to signal connect
        #would also work, but that wouldn't remove the deferences after Channel itself is deleted
        self._connectors = []

        for signal_name, receiver in self.__class__.receivers:
            #TODO use kind of a binder
            def make_connector(*args, **kwargs):
                return self.receive(receiver, *args, **kwargs)
            blinker.signal(signal_name % name).connect(make_connector)
            self._connectors.append(make_connector)

    def instance_subscribe(self, connection):
        self.connections.add(connection)

    @classmethod
    def channel_name(cls):
        return cls.__name__.lower()

    @classmethod
    def register(cls):
        cls.instances = {}
        cls.receivers = []
        Channel.channels[cls.channel_name()] = cls

    @classmethod
    def subscribe(cls, user, connection, name):
        logger.debug("subscribing %s, %s, %s, %s", cls, user, connection, name)
        if not cls.has_permissions(user, name):
            logger.error("Cannot subscribe %s, %s, %s, %s" % (cls, user, connection, name))
        instance = cls.instances.get(name, None) or cls(name)
        instance.instance_subscribe(connection)
        return instance

    @classmethod
    def unsubscribe(cls, user, connection, name):
        logger.debug("unsubscribing %s, %s, %s, %s", cls, user, connection, name)
        instance = cls.instances[name]
        if not instance.connections:
            logger.debug("deleting instance %s, %s", cls, name)
            del cls.instances[name]

    @classmethod
    def has_permissions(cls, user, name):
        return True

    @classmethod
    def add_receiver(cls, signal_name, receiver):
        cls.receivers.append((signal_name, receiver,))

    def receive(self, receiver, *args, **kwargs):
        #TODO state a comment
        connection = self.connections.pop()  # TODO it is assumed that there is always a connection
        self.connections.add(connection)  # TODO ugly workaround
        #  (what about disconnecting?)
        result = receiver(self, *args, **kwargs)
        if result is None:
            return
        message = dict(
            channel='%s.%s' % (self.channel_name(), self.name,),
            **result
        )
        connection.broadcast(self.connections, message)


def receiver(signal_name):
    def decorator(method):
        method._signal_name = signal_name
        return method
    return decorator


#register channels basing on settings
#TODO move it to separate file to avoid circular dependency
for app in settings.INSTALLED_APPS:
    module_name = "%s.channels" % app
    try:
        module = importlib.import_module(module_name)
    except ImportError as x:
        if x.name != module_name:
            #reraise if the import_module above is not a source of the problem
            raise
