import bots
from django.conf import settings
import os

args = ['-A %s worker' % bots.__name__, '-B', '--schedule=' + os.path.join(settings.PROJECT_DIR, 'data', 'celerybeat-schedule.db')]
bots.app.worker_main(args)