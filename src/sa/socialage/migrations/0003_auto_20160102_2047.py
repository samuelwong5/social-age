# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialage', '0002_facebookuser_birthday'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.CharField(primary_key=True, unique=True, serialize=False, max_length=60)),
                ('name', models.CharField(max_length=100)),
                ('fb_id', models.CharField(max_length=30)),
                ('tw_id', models.CharField(max_length=30)),
                ('fb_handle', models.CharField(max_length=100)),
                ('tw_handle', models.CharField(max_length=100)),
                ('probs', models.CommaSeparatedIntegerField(max_length=10)),
            ],
        ),
        migrations.AlterField(
            model_name='facebookpagelike',
            name='page',
            field=models.ForeignKey(to='socialage.Page', related_name='likes'),
        ),
        migrations.AlterField(
            model_name='facebookuser',
            name='birthday',
            field=models.DateTimeField(verbose_name='birthday'),
        ),
        migrations.DeleteModel(
            name='FacebookPage',
        ),
    ]
