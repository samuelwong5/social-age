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
    ageUnder12 = models.FloatField()
    age12to13 = models.FloatField()
    age14to15 = models.FloatField()
    age16to17 = models.FloatField()
    age18to24 = models.FloatField()
    age25to34 = models.FloatField()
    age35to44 = models.FloatField()
    age45to54 = models.FloatField()
    age55to64 = models.FloatField()
    ageAbove65 = models.FloatField()
    total = models.FloatField()


class FacebookPageLike(models.Model):
    user = models.ForeignKey(FacebookUser, related_name='liked_pages')
    page = models.ForeignKey(Page, related_name='likes')
    time = models.DateTimeField('date_liked')
