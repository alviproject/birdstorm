# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_task_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ship',
            name='system',
        ),
        migrations.AddField(
            model_name='ship',
            name='planet',
            field=models.ForeignKey(default=1, to='core.Planet'),
            preserve_default=True,
        ),
    ]
