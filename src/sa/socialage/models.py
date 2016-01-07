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
    probs = models.CommaSeparatedIntegerField(max_length=10)
    
class FacebookPageLike(models.Model):
    user = models.ForeignKey(User, related_name='liked_pages')
    page = models.ForeignKey(Page, related_name='likes')
    time = models.DateTimeField('date_liked')

class TwitterFollow(models.Model):
    user = models.ForeignKey(User, related_name='followed_pages')
    page = models.ForeignKey(Page, related_name='followers')

