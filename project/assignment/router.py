from api.viewsets import GroupViewSet, PhotoViewSet, LoginView, LogoutView
from rest_framework import routers
from django.urls import path, re_path, include

router = routers.DefaultRouter()
router.register('groups', GroupViewSet, basename="groups")
router.register('photos', PhotoViewSet, basename="photos")

urlpatterns = [
    path('', include(router.urls)),
]
