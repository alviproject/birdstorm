# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import concurrency.fields


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='version',
            field=concurrency.fields.IntegerVersionField(default=1, help_text='record revision number'),
            preserve_default=True,
        ),
    ]
