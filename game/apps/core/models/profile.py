from collections import OrderedDict
from django.contrib.auth.models import User
from django.db.models.fields import PositiveIntegerField
from django.db.models.signals import post_save
from jsonfield.fields import JSONField
from jsonschema import validate
import django.db.models as models


#TODO move to other file (this is a generic schema)
schema_resources = {
    "type": "object",
    "properties": {
        "Coal": {"type": "number", "minimum": 0, },
        "Iron": {"type": "number", "minimum": 0, },
        "Bauxite": {"type": "number", "minimum": 0, },
        "Oil": {"type": "number", "minimum": 0, },
        "Steel": {"type": "number", "minimum": 0, },
        "Aluminium": {"type": "number", "minimum": 0, },
        "Polymer": {"type": "number", "minimum": 0, },
    },
    "additionalProperties": True,  # TODO
}

#TODO not used at the moment
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
            "additionalProperties": True,  # TODO
        },
    },
    "additionalProperties": True,  # TODO
}


class Profile(models.Model):
    user = models.OneToOneField(User)
    data = JSONField(default={})
    credits = PositiveIntegerField(default=0)

    def is_drilled(self, planet_id):
        return self.data.get('drilled_planets', []).count(planet_id) > 0

    def get_scan_results(self, planet_id):
        results = self.data.get('scan_results', OrderedDict())
        return results.get(str(planet_id), [])

    def set_scan_result(self, planet_id, level, resources):
        scan_results = self.data.setdefault('scan_results', OrderedDict())
        if len(scan_results) >= 5:
            #keep only latest 5 scan results
            #FIXME popitem() takes no arguments (1 given)
            #scan_results.popitem(0)
            pass
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
        if len(planets) >= 2:
            planets.pop(0)
        planets.append(planet_id)
        del self.data['scan_results']


def create_profile(sender, instance, created, **kwargs):
    if created and not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance)


post_save.connect(create_profile, sender=User, dispatch_uid="create_profile")