from django.db import models
from django.db.models.query import QuerySet
from django_group_by import GroupByMixin


class FlickrModel(models.Model):
    '''
    Model which has all the fields present in a groupset.
    user field is the userId obtained from a session.  
    '''
    groupId = models.TextField()
    photoId = models.BigIntegerField()
    owner = models.TextField()
    secret = models.TextField()
    server = models.IntegerField()
    farm = models.IntegerField()
    title = models.TextField()
    isPublic = models.BooleanField()
    isFriend = models.BooleanField()
    isFamily = models.BooleanField()
    ownerName = models.TextField()
    dateAddedSeconds = models.BigIntegerField()
    img = models.ImageField(upload_to="pics/")
    userId = models.IntegerField()
