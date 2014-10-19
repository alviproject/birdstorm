import rest_framework.fields
from sockjs.tornado.basehandler import BaseHandler

#TODO add a comment
from sockjs.tornado.transports.websocket import WebSocketTransport


def strip_multiple_choice_msg(_):
    return ''

rest_framework.fields.strip_multiple_choice_msg = strip_multiple_choice_msg


#mitigates following exception raised when any error will occur during processing SockJS message
# > AttributeError: 'WebSocketTransport' object has no attribute 'abort_connection'
def abort_connection(*args, **kwargs):
    pass


WebSocketTransport.abort_connection = abort_connection


#TODO send pull request to sockjs-tornado
def finish(self, *args, **kwargs):
    """Tornado `finish` handler"""
    self._log_disconnect()

    super(BaseHandler, self).finish(*args, **kwargs)

BaseHandler.finish = finish


