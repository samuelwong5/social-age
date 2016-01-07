from django.db import models
from datetime import datetime
from uuid import uuid4

def char_uuid4():
    return str(uuid4())

class User(models.Model):
    id = models.CharField(primary_key=True, max_length=100, blank=True, unique=True, default=char_uuid4)
    fb_id = models.CharField(max_length=60)
    tw_id = models.CharField(max_length=60)
    name = models.CharField(max_length=100)
    birthday = models.DateTimeField(default=datetime.now)


class Page(models.Model):
    id = models.CharField(primary_key=True, max_length=100, unique=True, blank=True, default=char_uuid4)
    name = models.CharField(max_length=100)
    fb_id = models.CharField(max_length=30)
    tw_id = models.CharField(max_length=30)
    fb_handle = models.CharField(max_length=100)
    tw_handle = models.CharField(max_length=100)
    ageUnder12 = models.FloatField(default=0)
    age12to13 = models.FloatField(default=0)
    age14to15 = models.FloatField(default=0)
    age16to17 = models.FloatField(default=0)
    age18to24 = models.FloatField(default=0)
    age25to34 = models.FloatField(default=0)
    age35to44 = models.FloatField(default=0)
    age45to54 = models.FloatField(default=0)
    age55to64 = models.FloatField(default=0)
    ageAbove65 = models.FloatField(default=0)
    total = models.FloatField(default=0)


class FacebookPageLike(models.Model):
    user = models.ForeignKey(User, related_name='liked_pages')
    page = models.ForeignKey(Page, related_name='likes')
    time = models.DateTimeField('date_liked')

class TwitterFollow(models.Model):
    user = models.ForeignKey(User, related_name='followed_pages')
    page = models.ForeignKey(Page, related_name='followers')
