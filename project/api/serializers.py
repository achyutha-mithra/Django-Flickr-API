# from django.contrib.sites.models import get_current_site
from rest_framework import serializers
from data_load.models import FlickrModel
from django.db.models import Count
from rest_framework import exceptions
from django.contrib.auth import authenticate
import socket
from django.conf import settings
# from api.viewsets import b


class FlickrModelSerializer(serializers.HyperlinkedModelSerializer):
    '''
    This serializer provides info about a particular photoId.
    '''

    img = serializers.SerializerMethodField()

    class Meta:
        model = FlickrModel
        fields = ('groupId', 'photoId', 'owner', 'secret', 'server', 'farm', 'title',
                  'isPublic', 'isFriend', 'isFamily', 'ownerName', 'dateAddedSeconds', 'img')

    def get_img(self, obj):
        path = self.context.get("path")
        return "http://"+path+"/media/"+obj["img"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):

    '''
    This serializer has two fields, groupId and the count. Count is the number of photos a groupId has.
    '''

    count = serializers.SerializerMethodField()

    class Meta:
        model = FlickrModel
        fields = ('groupId', 'count')

    def get_count(self, obj):
        return obj['total']


class PerGroupImageViewSerializer(serializers.ModelSerializer):
    '''
    Has three fields, used when a groupId is provided to seggregate photos based on groupId.
    '''
    img = serializers.SerializerMethodField()

    class Meta:
        model = FlickrModel
        fields = ('photoId', 'title', 'img')

    def get_img(self, obj):
        path = self.context.get("path")
        return "http://"+path+"/media/"+obj["img"]


class PhotoSerializer(serializers.HyperlinkedModelSerializer):

    '''
    Default serializer for api/v1/photos/
    Lists all photos
    '''

    class Meta:
        model = FlickrModel
        fields = ('photoId',)


class LoginSerializer(serializers.Serializer):

    '''
    Validates username and password. Returns user if
    i. username and/or password are not empty
    ii. if the credentials are correct
    iii. if the user is active.
    '''
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username", "")
        password = data.get("password", "")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data["user"] = user
                else:
                    msg = "Account is disabled"
                    raise exceptions.ValidationError(msg)
            else:
                msg = "wrong credentials"
                raise exceptions.ValidationError(msg)
        else:
            msg = "Username and password not provided"
            raise exceptions.ValidationError(msg)

        return data
