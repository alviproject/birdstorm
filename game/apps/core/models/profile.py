from collections import OrderedDict
from django.contrib.auth.models import User
from jsonfield.fields import JSONField


class Profile:
    def __init__(self, user):
        self.user = user

    @property
    def data(self):
        return self.user.data

    def is_drilled(self, planet_id):
        return self.data.get('drilled_planets', []).count(planet_id) > 0

    def get_scan_results(self, planet_id):
        results = self.data.get('scan_results', OrderedDict())
        return results.get(str(planet_id), [])

    def set_scan_result(self, planet_id, level, resources):
        scan_results = self.data.setdefault('scan_results', OrderedDict())
        if len(scan_results) >= 5:
            #keep only latest 5 scan results
            scan_results.popitem(0)
        levels = scan_results.setdefault(str(planet_id), [])
        try:
            levels[level] = resources
        except IndexError:
            if len(levels) < level:
                #we can only add level by level
                raise RuntimeError()
            levels.append(resources)

    def add_drilled_planet(self, planet_id):
        planets = self.data.setdefault('drilled_planets', [])
        if planets.count(planet_id) > 0:
            return
        if len(planets) > 5:
            planets.pop(0)
        planets.append(planet_id)

    def save(self):
        self.user.save()


@property
def profile(self):
    return Profile(self)


User.profile = profile
JSONField().contribute_to_class(User, 'data')