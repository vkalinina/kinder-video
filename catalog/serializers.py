from rest_framework import serializers
from .models import Category, Video, ChildProfile, WatchHistory


class CategorySerializer(serializers.ModelSerializer):
    video_count = serializers.IntegerField(source="videos.count", read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "color",
            "icon",
            "order",
            "is_active",
            "video_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class VideoSerializer(serializers.ModelSerializer):
    embed_url = serializers.ReadOnlyField()
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Video
        fields = [
            "id",
            "category",
            "category_name",
            "title",
            "slug",
            "description",
            "youtube_url",
            "youtube_id",
            "thumbnail",
            "order",
            "is_active",
            "duration_seconds",
            "embed_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "embed_url", "created_at", "updated_at"]

    def validate_category(self, category):
        """Ensure the category belongs to the current user."""
        request = self.context.get("request")
        if request and category.owner != request.user:
            raise serializers.ValidationError(
                "You can only assign videos to your own categories."
            )
        return category


class VideoListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (no heavy fields)."""

    embed_url = serializers.ReadOnlyField()

    class Meta:
        model = Video
        fields = [
            "id",
            "category",
            "title",
            "slug",
            "youtube_id",
            "thumbnail",
            "order",
            "is_active",
            "duration_seconds",
            "embed_url",
        ]


class ChildProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildProfile
        fields = [
            "id",
            "name",
            "pin_code",
            "daily_limit_minutes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            # Never expose the PIN in read responses
            "pin_code": {"write_only": True},
        }


class WatchHistorySerializer(serializers.ModelSerializer):
    video_title = serializers.CharField(source="video.title", read_only=True)
    child_name = serializers.CharField(source="child.name", read_only=True)

    class Meta:
        model = WatchHistory
        fields = [
            "id",
            "child",
            "child_name",
            "video",
            "video_title",
            "watched_at",
            "watched_seconds",
        ]
        read_only_fields = ["id", "watched_at"]

    def validate_child(self, child):
        """Ensure the child profile belongs to the current user."""
        request = self.context.get("request")
        if request and child.owner != request.user:
            raise serializers.ValidationError(
                "You can only log watch history for your own children."
            )
        return child
