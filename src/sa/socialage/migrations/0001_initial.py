# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FacebookPage',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, max_length=30, unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='FacebookPageLike',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('time', models.DateTimeField(verbose_name='date_liked')),
                ('page', models.ForeignKey(to='socialage.FacebookPage', related_name='likes')),
            ],
        ),
        migrations.CreateModel(
            name='FacebookUser',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, max_length=30, unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='facebookpagelike',
            name='user',
            field=models.ForeignKey(to='socialage.FacebookUser', related_name='liked_pages'),
        ),
    ]
