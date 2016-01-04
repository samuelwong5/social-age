from django.db import models


class FacebookUser(models.Model):
    id = models.CharField(primary_key=True, max_length=30, unique=True)
    name = models.CharField(max_length=100)
    birthday = models.DateTimeField('birthday')

class Page(models.Model):
    id = models.CharField(primary_key=True, max_length=60, unique=True)
    name = models.CharField(max_length=100)
    fb_id = models.CharField(max_length=30)
    tw_id = models.CharField(max_length=30)
    fb_handle = models.CharField(max_length=100)
    tw_handle = models.CharField(max_length=100)
    probs = models.CommaSeparatedIntegerField(max_length=10)
    
class FacebookPageLike(models.Model):
    user = models.ForeignKey(FacebookUser, related_name='liked_pages')
    page = models.ForeignKey(Page, related_name='likes')
    time = models.DateTimeField('date_liked')