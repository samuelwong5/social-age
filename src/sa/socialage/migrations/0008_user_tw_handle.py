# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialage', '0007_auto_20160112_1835'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tw_handle',
            field=models.CharField(default=-1, max_length=100),
        ),
    ]
