# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models, migrations
from django.utils.timezone import utc


class Migration(migrations.Migration):
    dependencies = [
        ('socialage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='facebookuser',
            name='birthday',
            field=models.DateTimeField(verbose_name='date_liked',
                                       default=datetime.datetime(2015, 10, 22, 10, 41, 55, 873134, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
