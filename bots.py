import game.config
import tornado.options

game.config.configure()

from django.conf import settings
from celery import Celery
import requests
from datetime import timedelta

app = Celery('tasks', broker=settings.BROKER_URL)

service_url = "http://%s:%d" % (tornado.options.options.address, tornado.options.options.port)


class Service:
    def __init__(self, url, token):
        self.url = url
        self.headers = dict(
            Authorization='Token ' + token
        )

    def get(self, url):
        return requests.get(self.url+url, headers=self.headers)

    def post(self, url, data):
        return requests.post(self.url+url, data=data, headers=self.headers)


@app.task
def move(token, ship, systems):
    service = Service(service_url, token)
    response = service.get('/api/core/own_ships/%d/' % ship)
    current_system = response.json()['system_id']
    try:
        pos = systems.index(current_system)
    except ValueError:
        pos = 0
    next_system = systems[(pos+1) % len(systems)]
    service.post('/api/core/own_ships/%d/move/' % ship, dict(system_id=next_system))


app.conf.CELERYBEAT_SCHEDULE['add1'] = dict(
    task='bots.move',
    schedule=timedelta(seconds=7),
    kwargs=dict(
        token='34ca10122df90774e853f161d521c224f64e0dae',
        ship=1,
        systems=[2, 4, 6, 8, 10, 12],
    ),
)

app.conf.CELERYBEAT_SCHEDULE['add2'] = dict(
    task='bots.move',
    schedule=timedelta(seconds=17),
    kwargs=dict(
        token='0f44d6823d158416500dd5d1bf2d6f65df4ec869',
        ship=2,
        systems=[1, 3, 5, 7, 9, 11, 13],
    ),
)

app.conf.CELERYBEAT_SCHEDULE['add3'] = dict(
    task='bots.move',
    schedule=timedelta(seconds=20),
    kwargs=dict(
        token='34bf59a731ee43db40ac1d2e603c36c035b6ac7d',
        ship=3,
        systems=[13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
    ),
)

app.conf.CELERYBEAT_SCHEDULE['add4'] = dict(
    task='bots.move',
    schedule=timedelta(seconds=22),
    kwargs=dict(
        token='56f879426ad79431b15bbcc3300180a28c9d4fd2',
        ship=4,
        systems=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    ),
)



