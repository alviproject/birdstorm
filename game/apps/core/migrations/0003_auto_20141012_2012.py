# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_auto_20141009_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('type', models.CharField(max_length=255, help_text=None)),
                ('data', jsonfield.fields.JSONField(default={})),
                ('state', models.CharField(max_length=256, default='started')),
                ('archived', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='BlackDraft',
        ),
        migrations.DeleteModel(
            name='BlueDraft',
        ),
        migrations.DeleteModel(
            name='BrownDraft',
        ),
        migrations.DeleteModel(
            name='Draft',
        ),
        migrations.DeleteModel(
            name='RedDraft',
        ),
        migrations.DeleteModel(
            name='WhiteDraft',
        ),
        migrations.CreateModel(
            name='BlackDwarf',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='BlueDwarf',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='BrownDwarf',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='Dwarf',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='FirstScan',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.task',),
        ),
        migrations.CreateModel(
            name='IcePlanet',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.planet',),
        ),
        migrations.CreateModel(
            name='RedDwarf',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='RedPlanet',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.planet',),
        ),
        migrations.CreateModel(
            name='WaterPlanet',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.planet',),
        ),
        migrations.CreateModel(
            name='WhiteDwarf',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.AlterField(
            model_name='planet',
            name='x',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='planet',
            name='y',
            field=models.FloatField(),
        ),
    ]
