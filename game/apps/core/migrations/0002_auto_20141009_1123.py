# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Owl',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.ship',),
        ),
        migrations.CreateModel(
            name='Swallow',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.ship',),
        ),
        migrations.AddField(
            model_name='planet',
            name='x',
            field=models.FloatField(default=0.1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='planet',
            name='y',
            field=models.FloatField(default=-0.1),
            preserve_default=True,
        ),
    ]
