#!/usr/bin/env python
import os
import sys

#TODO duplicated in run.py
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

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
