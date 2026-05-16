from rest_framework import serializers

from .models import Category, Video, ChildProfile, WatchHistory


class CategorySerializer(serializers.ModelSerializer):
    video_count = serializers.IntegerField(source="videos.count", read_only=True)

    icon = serializers.ImageField(
        required=False,
        allow_null=True,
        write_only=True
    )
    icon_url = serializers.ImageField(
        source="icon",
        read_only=True
    )
    order = serializers.IntegerField(min_value=0, max_value=32767, default=0)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "color",
            "icon",
            "icon_url",
            "order",
            "is_active",
            "video_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class VideoSerializer(serializers.ModelSerializer):
    embed_url = serializers.ReadOnlyField()

    # Выпадающий список категорий — только категории текущего пользователя
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.none(),  # queryset переопределяется в __init__
    )
    category_name = serializers.CharField(source="category.name", read_only=True)

    # Явно ImageField для Swagger — кнопка загрузки файла
    thumbnail = serializers.ImageField(required=False, allow_null=True, use_url=True)

    # Нормальные диапазоны для числовых полей
    order = serializers.IntegerField(min_value=0, max_value=32767, default=0)
    duration_seconds = serializers.IntegerField(
        min_value=0, max_value=86400, required=False, allow_null=True
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем категории по текущему пользователю — так в Swagger
        # выпадающий список покажет только свои категории
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["category"].queryset = Category.objects.filter(
                owner=request.user
            )

    def validate_category(self, category):
        """Категория должна принадлежать текущему пользователю."""
        request = self.context.get("request")
        if request and category.owner != request.user:
            raise serializers.ValidationError(
                "You can only assign videos to your own categories."
            )
        return category


class VideoListSerializer(serializers.ModelSerializer):
    """Лёгкий сериалайзер для list-экшенов."""

    embed_url = serializers.ReadOnlyField()
    thumbnail = serializers.ImageField(required=False, allow_null=True, use_url=True)
    order = serializers.IntegerField(min_value=0, max_value=32767, default=0)

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
    daily_limit_minutes = serializers.IntegerField(
        min_value=0,
        max_value=1440,
        required=False,
        allow_null=True,
        help_text="Дневной лимит просмотра в минутах (макс. 1440 = 24 часа).",
    )

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
            "pin_code": {"write_only": True},
        }


class WatchHistorySerializer(serializers.ModelSerializer):
    video_title = serializers.CharField(source="video.title", read_only=True)
    child_name = serializers.CharField(source="child.name", read_only=True)
    watched_seconds = serializers.IntegerField(min_value=0, max_value=86400, default=0)

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
        """Профиль ребёнка должен принадлежать текущему пользователю."""
        request = self.context.get("request")
        if request and child.owner != request.user:
            raise serializers.ValidationError(
                "You can only log watch history for your own children."
            )
        return child
