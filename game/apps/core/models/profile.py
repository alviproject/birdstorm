from django.contrib.auth.models import User
from django.db import models
from jsonfield.fields import JSONField


class Profile:
    def __init__(self, user):
        self.user = user

    def is_drilled(self, planet_id):
            try:
                return self.user.data['drilled_planets'].count(planet_id) > 0
            except KeyError:
                return False

    def scan_results(self, planet_id):
        results = self.user.data.get('scan_results', [])
        for r in results:
            if r['planet_id'] == planet_id:
                return r['levels']
        return []

    def set_scan_result(self, planet_id, level, resources):
        scan_results = self.user.data.setdefault('scan_results', [])
        for r in scan_results:
            if r['planet_id'] == planet_id:
                result = r
                break
        else:
            if len(scan_results) >= 5:
                scan_results.pop(0)
            result = dict(
                planet_id=planet_id,
                levels=[],
            )
            scan_results.append(result)
        levels = result['levels']
        try:
            levels[level] = resources
        except IndexError:
            if len(levels) < level:
                raise RuntimeError()
            levels.append(resources)

    def save(self):
        self.user.save()


@property
def profile(self):
    return Profile(self)


User.profile = profile
JSONField().contribute_to_class(User, 'data')