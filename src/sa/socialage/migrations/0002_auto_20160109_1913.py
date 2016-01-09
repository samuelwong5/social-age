# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='social_age',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
    ]
