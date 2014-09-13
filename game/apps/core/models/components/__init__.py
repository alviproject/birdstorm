from game.apps.core.models.components.engines import Engine
from game.apps.core.models.components.drills import Drill
from game.apps.core.models.components.scanners import Scanner


def create_kind(kind):
    if kind == 'Engine':
        return Engine
    elif kind == 'Drill':
        return Drill
    elif kind == 'Scanner':
        return Scanner
    else:
        raise RuntimeError("Unknown component kind: " + kind)
