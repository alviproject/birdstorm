from datetime import timedelta
from rest_framework.decorators import action
import tornado.ioloop
from rest_framework.response import Response


def async_action(wrapped_action):
    def step(it):
        #TODO check if time is as expected when task is actually launched, issue a warning if it isn't
        try:
            time_delta = next(it)
        except StopIteration:
            return
        tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=time_delta), step, it)

    def wrapper(model, request, *args, **kwargs):
        it = wrapped_action(model, request, *args, **kwargs)
        step(it)
        return Response()

    return action()(wrapper)