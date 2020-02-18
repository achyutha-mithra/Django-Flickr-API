from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from rest_framework.renderers import TemplateHTMLRenderer
from django.contrib.auth import login as django_login, logout as django_logout
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
import re
from data_load.models import FlickrModel
from api import serializers
from api.serializers import FlickrModelSerializer, GroupSerializer, PhotoSerializer, LoginSerializer, PerGroupImageViewSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Count
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.decorators import action, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from api.paginator_custom import StandardResultsSetPagination
from django.contrib.sites.shortcuts import get_current_site


class GroupViewSet(viewsets.ViewSet):

    '''
    Viewset for api/v1/groups, api/v1/<GID>.
    Authentication used: Session based on token authentication. 
    Custom paginator imported from paginator_custom.

    => list() funtion is used to display the groupId along with the number of images belonging to that groupId.
    => retrieve() function is used to fetch all the photos belonging to a particular group. 
    '''

    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated,)

    paginator = StandardResultsSetPagination()
    page_size = 15
    paginator.page_size = page_size

    def list(self, request):
        queryset = FlickrModel.objects.filter(userId=request.user.id).values(
            'groupId',).annotate(total=Count('photoId'))

        serializer = GroupSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):

        pk = re.sub("@", "%40", pk)
        queryset = FlickrModel.objects.filter(
            groupId=pk, userId=request.user.id).values('photoId', 'title', 'img')
        path = get_current_site(request).domain
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = PerGroupImageViewSerializer(
            result_page, many=True, context={'path': path})
        return self.paginator.get_paginated_response(serializer.data)


class PhotoViewSet(viewsets.ViewSet):
    '''
    Viewset for api/v1/photos, api/v1/photos/<ID>, api/v1/photos/?group=<GID>.
    Authentication used: Session based on token authentication. 
    Custom paginator imported from paginator_custom.

    => list(): 
        i) if group parameter is provider: Will fetch photos belonging to that group.
        ii) if group parameter is not provided: will fetch all photos
    => retrieve(): function is used to fetch information about a particular photoId. 
    '''
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated,)

    paginator = StandardResultsSetPagination()
    page_size = 15
    paginator.page_size = page_size

    def list(self, request, group=None):
        if request.GET.get("group") is not None:
            group = request.GET.get("group")
            main_id = re.sub("/", "", group)
            main_id = re.sub("@", "%40", main_id)
            path = get_current_site(request).domain
            if "?" in main_id:
                page_number = main_id.split("?")[1]
                page_number = int(
                    re.search('page=(.+?)$', page_number).group(1))
                main_id = main_id.split("?")[0]
            else:
                page_number = 1
            posts = FlickrModel.objects.filter(
                groupId=main_id, userId=request.user.id).values('title', 'img')
            paginator = Paginator(posts, 10)
            page = request.GET.get('page')
            posts = paginator.get_page(page_number)
            return render(request, "images_per_group.html", {'images': posts, 'path': path, 'gid': main_id})
        else:
            queryset = FlickrModel.objects.filter(
                userId=request.user.id).values('photoId')
            print(queryset)
            result_page = self.paginator.paginate_queryset(queryset, request)
            serializer = PhotoSerializer(result_page, many=True)
            return Response(serializer.data)

    def retrieve(self, request, pk=None):
        id_list = FlickrModel.objects.filter(
            photoId=pk, userId=request.user.id).values()
        path = get_current_site(request).domain
        serializer = FlickrModelSerializer(
            id_list, many=True, context={'path': path})
        return Response(serializer.data)


class LoginView(APIView):
    '''
    Will authenticate user by providing a unique token. Uses LoginSerializer to validate username and password.
    '''

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        django_login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=200)


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication, )

    def post(self, request):
        django_logout(request)
        return Response(status=204)
