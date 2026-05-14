from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, VideoViewSet, ChildProfileViewSet, WatchHistoryViewSet

app_name = "catalog"

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"videos", VideoViewSet, basename="video")
router.register(r"children", ChildProfileViewSet, basename="childprofile")
router.register(r"watch-history", WatchHistoryViewSet, basename="watchhistory")

urlpatterns = [
    path("", include(router.urls)),
]