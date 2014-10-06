import sys
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game.settings")

if os.path.exists(".env_local"):
    env_input = ".env_local"
else:
    print(".env_local does not exists, using default .env file")
    env_input = ".env"

with open(env_input) as env:
    for line in env.read().splitlines():
        if not line.strip():  # skip empty lines
            continue
        var = line.split('=')
        print(var)
        os.environ.setdefault(*var)

import logging
logging.basicConfig(level=logging.WARNING)

import game.utils.patch
import django
django.setup()

import game.server
import django.core.management


link = sys.platform != 'win32'
django.core.management.call_command('collectstatic', link=link, interactive=False)
django.core.management.call_command('migrate', interactive=False)
django.core.management.call_command('loaddata', os.path.join('game', 'apps', 'core', 'fixtures', 'initial_data.json'),  interactive=False)

game.server.main()

