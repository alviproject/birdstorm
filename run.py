import os
import sys
import os.path

if os.path.exists(".env_local"):
    env_input = ".env_local"
else:
    print(".env_local does not exists, using default .env file")
    env_input = ".env"

with open(env_input) as env:
    for line in env.read().splitlines():
        var = line.split('=')
        print(var)
        os.environ.setdefault(*var)

import game.server
import django.core.management


link = sys.platform != 'win32'
django.core.management.call_command('collectstatic', link=link, interactive=False)
game.server.main()

