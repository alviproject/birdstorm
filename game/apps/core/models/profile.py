from collections import OrderedDict
from django.contrib.auth.models import User
from django.db.models.fields import PositiveIntegerField
from jsonfield.fields import JSONField
from jsonschema import validate


#TODO move to other file (this is a generic schema)
schema_resources = {
    "type": "object",
    "properties": {
        "coal": {"type": "number", "minimum": 0, },
        "iron_ore": {"type": "number", "minimum": 0, },
    },
    "additionalProperties": False,
}

data_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",

    "type": "object",
    "properties": {
        "drilled_planets": {
            "type": "array",
            "items": {"type": "number", "minimum": 0},
            "maxItems": 5
        },
        "scan_results": {
            "type": "object",
            "patternProperties": {
                "[0-9]*": {
                    "type": "array",
                    "items": schema_resources,
                },
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False
}


class Profile:
    def __init__(self, user):
        self.user = user

    @property
    def data(self):
        # TODO thw whole if, the reason for this workaround is that if user is created from outside
        # (fe. by manage.py createsuperuser) then default value ('{}') is not taken into account and data is a string
        # instead of JSON, this could be fixed in JSONFiled
        if self.user.data == '':
            self.user.data = {}
        return self.user.data

    def is_drilled(self, planet_id):
        return self.data.get('drilled_planets', []).count(planet_id) > 0

    def warehouse_resources(self, warehouse_id):
        warehouses = self.data.setdefault('warehouses', dict())
        return warehouses.setdefault(warehouse_id, dict())

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
        del self.data['scan_results']

    def save(self):
        validate(self.data, data_schema)
        self.user.save()


@property
def profile(self):
    return Profile(self)


User.profile = profile
JSONField(default={}).contribute_to_class(User, 'data')
PositiveIntegerField(default=0).contribute_to_class(User, 'credits')
