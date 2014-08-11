from django.contrib.auth.models import User
from django.db import models
from jsonfield.fields import JSONField


class Profile:
    def __init__(self, user):
        self.user = user

    def is_drilled(self, planet_id):
            try:
                return self.user.data['mining_data']['drilled_planets'].count(planet_id) > 0
            except KeyError:
                return False

    def scan_result(self, planet_id):
        mining_data = self.user.data.setdefault('mining_data', dict(scan_results=[]))
        results = mining_data['scan_results']
        for r in results:
            if r['planet_id'] == planet_id:
                return r
        if len(results) >= 5:
            results.pop(0)
        result = dict(
            planet_id=planet_id,
            levels=[],
        )
        results.append(result)
        return result


@property
def profile(self):
    return Profile(self)


User.profile = profile
JSONField().contribute_to_class(User, 'data')