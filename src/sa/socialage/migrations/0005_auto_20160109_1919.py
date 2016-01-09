# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialage', '0004_auto_20160109_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='social_age',
            field=models.IntegerField(null=True),
        ),
    ]
