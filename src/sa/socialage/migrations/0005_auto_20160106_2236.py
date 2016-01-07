# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('socialage', '0004_auto_20160106_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='id',
            field=models.CharField(default=uuid.uuid4, serialize=False, max_length=100, unique=True, primary_key=True, blank=True),
        ),
    ]
