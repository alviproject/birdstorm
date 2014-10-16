# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import concurrency.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20141012_2012'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alloys',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.task',),
        ),
        migrations.CreateModel(
            name='Extraction',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.task',),
        ),
        migrations.CreateModel(
            name='Panels',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.task',),
        ),
        migrations.CreateModel(
            name='WhoAreYou',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.task',),
        ),
        migrations.CreateModel(
            name='WhoIAm',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.task',),
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ('-id',)},
        ),
        migrations.AddField(
            model_name='building',
            name='version',
            field=concurrency.fields.IntegerVersionField(default=1, help_text='record revision number'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='planet',
            name='version',
            field=concurrency.fields.IntegerVersionField(default=1, help_text='record revision number'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='version',
            field=concurrency.fields.IntegerVersionField(default=1, help_text='record revision number'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='system',
            name='version',
            field=concurrency.fields.IntegerVersionField(default=1, help_text='record revision number'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='version',
            field=concurrency.fields.IntegerVersionField(default=1, help_text='record revision number'),
            preserve_default=True,
        ),
    ]
