from rest_framework.generics import ListAPIView
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Video, ChildProfile, WatchHistory
from .serializers import (
    CategorySerializer,
    VideoSerializer,
    VideoListSerializer,
    ChildProfileSerializer,
    WatchHistorySerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for video categories.
    Each user only sees and manages their own categories.
    """

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["order", "name", "created_at"]
    ordering = ["order", "name"]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"])
    def videos(self, request, pk=None):
        """Return all videos belonging to this category."""
        category = self.get_object()
        videos = category.videos.filter(is_active=True)
        serializer = VideoListSerializer(videos, many=True, context={"request": request})
        return Response(serializer.data)


class VideoViewSet(viewsets.ModelViewSet):
    """
    CRUD for YouTube videos.
    Each user only sees and manages their own videos.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_active"]
    search_fields = ["title", "description", "youtube_id"]
    ordering_fields = ["order", "title", "created_at"]
    ordering = ["order", "title"]

    def get_queryset(self):
        return Video.objects.filter(owner=self.request.user).select_related("category")

    def get_serializer_class(self):
        if self.action == "list":
            return VideoListSerializer
        return VideoSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ChildProfileViewSet(viewsets.ModelViewSet):
    """
    CRUD for child profiles.
    Each user only sees and manages their own children.
    """

    serializer_class = ChildProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return ChildProfile.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"])
    def watch_history(self, request, pk=None):
        """Return the watch history for a specific child."""
        child = self.get_object()
        history = child.watch_history.select_related("video").all()
        serializer = WatchHistorySerializer(
            history, many=True, context={"request": request}
        )
        return Response(serializer.data)


class WatchHistoryViewSet(viewsets.ModelViewSet):
    """
    Log and retrieve watch history entries.
    Scoped to children that belong to the current user.
    """

    serializer_class = WatchHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["child", "video"]
    ordering_fields = ["watched_at", "watched_seconds"]
    ordering = ["-watched_at"]

    def get_queryset(self):
        return WatchHistory.objects.filter(
            child__owner=self.request.user
        ).select_related("child", "video")
