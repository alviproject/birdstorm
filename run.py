import os
import django.core.management
import sys
import game.server
import os.path

if os.path.isfile(".env_local"):
    env_input = ".env_local"
else:
    env_input = ".env"

with open(env_input) as env:
    for line in env.read().splitlines():
        var = line.split('=')
        print(var)
        os.environ.setdefault(*var)

link = sys.platform != 'win32'
django.core.management.call_command('collectstatic', link=link, interactive=False)
game.server.main()

