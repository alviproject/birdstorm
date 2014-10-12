from game.apps.core.models import Ship
from game.apps.core.models import Building
from game.apps.core.models import System
from game.apps.core.models import Planet
from game.apps.core.models import Profile
from game.apps.core.models import Task

from django.contrib import admin

admin.site.register(Ship)
admin.site.register(Building)
admin.site.register(System)
admin.site.register(Planet)
admin.site.register(Profile)
admin.site.register(Task)
