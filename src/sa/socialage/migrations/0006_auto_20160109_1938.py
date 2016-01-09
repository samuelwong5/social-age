# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialage', '0005_auto_20160109_1919'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fb_friends',
            field=models.CommaSeparatedIntegerField(max_length=100, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='fb_id',
            field=models.CharField(max_length=60, default=-1),
        ),
        migrations.AlterField(
            model_name='user',
            name='social_age',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='tw_id',
            field=models.CharField(max_length=60, default=-1),
        ),
    ]
