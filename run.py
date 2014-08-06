import os
import django.core.management
import game.server

with open(".env") as env:
    for line in env.read().splitlines():
        var = line.split('=')
        print(var)
        os.environ.setdefault(*var)

django.core.management.call_command('collectstatic', link=1, interactive=False)
game.server.main()

