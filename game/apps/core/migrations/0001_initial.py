# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings
import concurrency.fields
import game.utils.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(help_text=None, max_length=255)),
                ('level', models.IntegerField(default=1)),
                ('data', jsonfield.fields.JSONField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Planet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(help_text=None, max_length=255)),
                ('data', jsonfield.fields.JSONField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', jsonfield.fields.JSONField(default={})),
                ('credits', models.PositiveIntegerField(default=0)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(help_text=None, max_length=255)),
                ('data', jsonfield.fields.JSONField(default={})),
                ('locked', models.BooleanField(default=False)),
                ('version', concurrency.fields.IntegerVersionField(default=1, help_text='record revision number')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model, game.utils.models.ResourceContainer),
        ),
        migrations.CreateModel(
            name='System',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(help_text=None, max_length=255)),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ship',
            name='system',
            field=models.ForeignKey(to='core.System'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='planet',
            name='system',
            field=models.ForeignKey(to='core.System'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='building',
            name='planet',
            field=models.ForeignKey(related_name='buildings', to='core.Planet'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='BlackDraft',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='BlackHole',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='BlueDraft',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='BlueSuperGiant',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='BrownDraft',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='Draft',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='GasGiant',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.planet',),
        ),
        migrations.CreateModel(
            name='HyperGiant',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='Mine',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.building',),
        ),
        migrations.CreateModel(
            name='Nebula',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='NeutronStar',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.building', game.utils.models.ResourceContainer),
        ),
        migrations.CreateModel(
            name='Protostar',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.building',),
        ),
        migrations.CreateModel(
            name='Plant',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.provider',),
        ),
        migrations.CreateModel(
            name='Factory',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.plant',),
        ),
        migrations.CreateModel(
            name='Raven',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.ship',),
        ),
        migrations.CreateModel(
            name='RedDraft',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='RedGiant',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='Refinery',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.plant',),
        ),
        migrations.CreateModel(
            name='Shipyard',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.building',),
        ),
        migrations.CreateModel(
            name='Smelter',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.plant',),
        ),
        migrations.CreateModel(
            name='TerrestrialPlanet',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.planet',),
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.building',),
        ),
        migrations.CreateModel(
            name='WhiteDraft',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.system',),
        ),
        migrations.CreateModel(
            name='Workshop',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.provider',),
        ),
    ]
