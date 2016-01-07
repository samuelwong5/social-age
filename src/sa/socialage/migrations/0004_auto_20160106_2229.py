# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('socialage', '0003_auto_20160102_2047'),
    ]

    operations = [
        migrations.CreateModel(
            name='TwitterFollow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('page', models.ForeignKey(related_name='followers', to='socialage.Page')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.CharField(blank=True, primary_key=True, max_length=100, unique=True, serialize=False, default=uuid.uuid4)),
                ('fb_id', models.CharField(max_length=60)),
                ('tw_id', models.CharField(max_length=60)),
                ('name', models.CharField(max_length=100)),
                ('birthday', models.DateTimeField(verbose_name='birthday')),
            ],
        ),
        migrations.AlterField(
            model_name='facebookpagelike',
            name='user',
            field=models.ForeignKey(related_name='liked_pages', to='socialage.User'),
        ),
        migrations.DeleteModel(
            name='FacebookUser',
        ),
        migrations.AddField(
            model_name='twitterfollow',
            name='user',
            field=models.ForeignKey(related_name='followed_pages', to='socialage.User'),
        ),
    ]
