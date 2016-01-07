# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('socialage', '0006_auto_20160106_2250'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='probs',
        ),
        migrations.AddField(
            model_name='page',
            name='age12to13',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='page',
            name='age14to15',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='page',
            name='age16to17',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='page',
            name='age18to24',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='page',
            name='age25to34',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='page',
            name='age35to44',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='page',
            name='age45to54',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='page',
            name='age55to64',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='page',
            name='ageAbove65',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='page',
            name='ageUnder12',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='page',
            name='total',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='birthday',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
