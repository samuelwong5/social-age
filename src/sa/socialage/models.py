from django.db import models


class FacebookUser(models.Model):
    id = models.CharField(primary_key=True, max_length=30, unique=True)
    name = models.CharField(max_length=100)
    birthday = models.DateTimeField('birthday')

class FacebookPage(models.Model):
    id = models.CharField(primary_key=True, max_length=30, unique=True)
    name = models.CharField(max_length=100)
    
class FacebookPageLike(models.Model):
    user = models.ForeignKey(FacebookUser, related_name='liked_pages')
    page = models.ForeignKey(FacebookPage, related_name='likes')
    time = models.DateTimeField('date_liked')