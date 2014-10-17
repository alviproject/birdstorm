from collections import OrderedDict
from concurrency.fields import IntegerVersionField
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
    data = JSONField(default={}, load_kwargs={'object_pairs_hook': OrderedDict})
    credits = PositiveIntegerField(default=0)
    version = IntegerVersionField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.drilled_planets = [int(planet_id) for planet_id in self.data.get('drilled_planets', [])]
        self.scan_results = OrderedDict()

        #dict comprehension would not allow to keep order, hence for loop
        for planet_id, details in self.data.get('scan_results', OrderedDict()).items():
            #planet.id is an int value while JSON does not allow to use integers for dict keys, hence conversion
            self.scan_results[int(planet_id)] = details

    def save(self, *args, **kwargs):
        #TODO this causes problems in admin panel
        self.data = {
            'drilled_planets': self.drilled_planets,
            'scan_results': self.scan_results,
        }
        super().save(*args, **kwargs)

    def is_drilled(self, planet_id):
        return self.drilled_planets.count(planet_id) > 0

    def set_scan_result(self, planet_id, level, resources):
        if len(self.scan_results) >= 5:
            #keep only latest 5 scan results
            self.scan_results.popitem(0)
        levels = self.scan_results.setdefault(planet_id, [])
        try:
            levels[level] = resources
        except IndexError:
            if len(levels) < level:
                #we can only add level by level
                raise RuntimeError()
            levels.append(resources)

    def add_drilled_planet(self, planet_id):
        if self.drilled_planets.count(planet_id) > 0:
            return
        if len(self.drilled_planets) >= 2:
            self.drilled_planets.pop(0)
        self.drilled_planets.append(planet_id)
        del self.scan_results[planet_id]


def create_profile(sender, instance, created, **kwargs):
    if created and not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance)


post_save.connect(create_profile, sender=User, dispatch_uid="create_profile")