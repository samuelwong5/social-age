# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import socialage.models


class Migration(migrations.Migration):

    dependencies = [
        ('socialage', '0005_auto_20160106_2236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='id',
            field=models.CharField(primary_key=True, blank=True, max_length=100, serialize=False, unique=True, default=socialage.models.char_uuid4),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.CharField(primary_key=True, blank=True, max_length=100, serialize=False, unique=True, default=socialage.models.char_uuid4),
        ),
    ]
