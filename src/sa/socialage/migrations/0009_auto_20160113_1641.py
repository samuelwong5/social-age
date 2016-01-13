# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialage', '0008_user_tw_handle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='tw_handle',
            field=models.CharField(default='', max_length=100),
        ),
    ]
