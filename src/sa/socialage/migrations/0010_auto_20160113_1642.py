# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialage', '0009_auto_20160113_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='tw_id',
            field=models.CharField(max_length=30),
        ),
    ]
