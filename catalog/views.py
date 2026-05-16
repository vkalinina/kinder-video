from rest_framework import viewsets, filters, status, parsers
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes

from .models import Category, Video, ChildProfile, WatchHistory
from .serializers import (
    CategorySerializer,
    VideoSerializer,
    VideoListSerializer,
    ChildProfileSerializer,
    WatchHistorySerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Список категорий",
        description="Возвращает все категории текущего пользователя. "
        "Поддерживает поиск по названию и описанию, сортировку.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                description="Поиск по полям name и description.",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                description="Сортировка: `order`, `name`, `created_at`. "
                "Для обратного порядка добавьте `-` (например `-created_at`).",
            ),
        ],
        responses={200: CategorySerializer(many=True)},
        tags=["Categories"],
    ),
    create=extend_schema(
        summary="Создать категорию",
        description="Создаёт новую категорию для текущего пользователя. "
        "Поле `owner` подставляется автоматически.",
        request=CategorySerializer,
        responses={
            201: CategorySerializer,
            400: OpenApiResponse(description="Ошибка валидации данных."),
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "name": "Мультфильмы",
                    "description": "Любимые мультики",
                    "color": "#FF6B6B",
                    "order": 1,
                    "is_active": True,
                },
                request_only=True,
            )
        ],
        tags=["Categories"],
    ),
    retrieve=extend_schema(
        summary="Получить категорию",
        description="Возвращает одну категорию по `id`.",
        responses={
            200: CategorySerializer,
            404: OpenApiResponse(description="Категория не найдена."),
        },
        tags=["Categories"],
    ),
    update=extend_schema(
        summary="Обновить категорию (PUT)",
        description="Полное обновление категории. Все поля обязательны.",
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: OpenApiResponse(description="Ошибка валидации."),
            404: OpenApiResponse(description="Категория не найдена."),
        },
        tags=["Categories"],
    ),
    partial_update=extend_schema(
        summary="Обновить категорию (PATCH)",
        description="Частичное обновление категории. Можно передать только изменяемые поля.",
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: OpenApiResponse(description="Ошибка валидации."),
            404: OpenApiResponse(description="Категория не найдена."),
        },
        tags=["Categories"],
    ),
    destroy=extend_schema(
        summary="Удалить категорию",
        description="Удаляет категорию вместе со всеми привязанными видео (CASCADE).",
        responses={
            204: OpenApiResponse(description="Категория удалена."),
            404: OpenApiResponse(description="Категория не найдена."),
        },
        tags=["Categories"],
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD для категорий видео. Пользователь видит только свои категории."""

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["order", "name", "created_at"]
    ordering = ["order", "name"]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        summary="Обновить категорию (PUT)",
        description="Полное обновление категории.",
        request={"multipart/form-data": CategorySerializer},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Видео категории",
        description="Возвращает список активных видео, принадлежащих данной категории.",
        responses={
            200: VideoListSerializer(many=True),
            404: OpenApiResponse(description="Категория не найдена."),
        },
        tags=["Categories"],
    )
    @action(detail=True, methods=["get"])
    def videos(self, request, pk=None):
        category = self.get_object()
        videos = category.videos.filter(is_active=True)
        serializer = VideoListSerializer(
            videos, many=True, context={"request": request}
        )
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Список видео",
        description="Возвращает краткий список видео текущего пользователя. "
        "Поддерживает фильтрацию по категории и статусу, поиск и сортировку.",
        parameters=[
            OpenApiParameter(
                name="category",
                type=OpenApiTypes.INT,
                description="Фильтр по ID категории.",
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                description="Фильтр по статусу активности.",
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                description="Поиск по title, description, youtube_id.",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                description="Сортировка: `order`, `title`, `created_at`.",
            ),
        ],
        responses={200: VideoListSerializer(many=True)},
        tags=["Videos"],
    ),
    create=extend_schema(
        summary="Добавить видео",
        description="Создаёт новую запись YouTube-видео для текущего пользователя.",
        request=VideoSerializer,
        responses={
            201: VideoSerializer,
            400: OpenApiResponse(description="Ошибка валидации данных."),
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "category": 1,
                    "title": "Маша и Медведь — серия 1",
                    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "youtube_id": "dQw4w9WgXcQ",
                    "description": "Первая серия",
                    "order": 1,
                    "is_active": True,
                    "duration_seconds": 420,
                },
                request_only=True,
            )
        ],
        tags=["Videos"],
    ),
    retrieve=extend_schema(
        summary="Получить видео",
        description="Возвращает полные данные одного видео по `id`.",
        responses={
            200: VideoSerializer,
            404: OpenApiResponse(description="Видео не найдено."),
        },
        tags=["Videos"],
    ),
    update=extend_schema(
        summary="Обновить видео (PUT)",
        description="Полное обновление видео. Все поля обязательны.",
        request=VideoSerializer,
        responses={
            200: VideoSerializer,
            400: OpenApiResponse(description="Ошибка валидации."),
            404: OpenApiResponse(description="Видео не найдено."),
        },
        tags=["Videos"],
    ),
    partial_update=extend_schema(
        summary="Обновить видео (PATCH)",
        description="Частичное обновление видео.",
        request=VideoSerializer,
        responses={
            200: VideoSerializer,
            400: OpenApiResponse(description="Ошибка валидации."),
            404: OpenApiResponse(description="Видео не найдено."),
        },
        tags=["Videos"],
    ),
    destroy=extend_schema(
        summary="Удалить видео",
        description="Удаляет видео и его историю просмотров (CASCADE).",
        responses={
            204: OpenApiResponse(description="Видео удалено."),
            404: OpenApiResponse(description="Видео не найдено."),
        },
        tags=["Videos"],
    ),
)
class VideoViewSet(viewsets.ModelViewSet):
    """CRUD для YouTube-видео. Пользователь видит только свои видео."""

    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
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


@extend_schema_view(
    list=extend_schema(
        summary="Список профилей детей",
        description="Возвращает все детские профили текущего пользователя.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                description="Поиск по имени ребёнка.",
            ),
        ],
        responses={200: ChildProfileSerializer(many=True)},
        tags=["Children"],
    ),
    create=extend_schema(
        summary="Создать профиль ребёнка",
        description="Создаёт новый детский профиль. "
        "Поле `pin_code` — опционально, только для записи.",
        request=ChildProfileSerializer,
        responses={
            201: ChildProfileSerializer,
            400: OpenApiResponse(description="Ошибка валидации."),
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "name": "Анна",
                    "pin_code": "1234",
                    "daily_limit_minutes": 60,
                    "is_active": True,
                },
                request_only=True,
            )
        ],
        tags=["Children"],
    ),
    retrieve=extend_schema(
        summary="Получить профиль ребёнка",
        description="Возвращает данные одного детского профиля по `id`.",
        responses={
            200: ChildProfileSerializer,
            404: OpenApiResponse(description="Профиль не найден."),
        },
        tags=["Children"],
    ),
    update=extend_schema(
        summary="Обновить профиль ребёнка (PUT)",
        description="Полное обновление профиля ребёнка.",
        request=ChildProfileSerializer,
        responses={
            200: ChildProfileSerializer,
            400: OpenApiResponse(description="Ошибка валидации."),
            404: OpenApiResponse(description="Профиль не найден."),
        },
        tags=["Children"],
    ),
    partial_update=extend_schema(
        summary="Обновить профиль ребёнка (PATCH)",
        description="Частичное обновление профиля ребёнка.",
        request=ChildProfileSerializer,
        responses={
            200: ChildProfileSerializer,
            400: OpenApiResponse(description="Ошибка валидации."),
            404: OpenApiResponse(description="Профиль не найден."),
        },
        tags=["Children"],
    ),
    destroy=extend_schema(
        summary="Удалить профиль ребёнка",
        description="Удаляет профиль ребёнка вместе с его историей просмотров.",
        responses={
            204: OpenApiResponse(description="Профиль удалён."),
            404: OpenApiResponse(description="Профиль не найден."),
        },
        tags=["Children"],
    ),
)
class ChildProfileViewSet(viewsets.ModelViewSet):
    """CRUD для детских профилей. Пользователь видит только своих детей."""

    serializer_class = ChildProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return ChildProfile.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        summary="История просмотров ребёнка",
        description="Возвращает полную историю просмотров для конкретного детского профиля, "
        "отсортированную от новых к старым.",
        responses={
            200: WatchHistorySerializer(many=True),
            404: OpenApiResponse(description="Профиль не найден."),
        },
        tags=["Children"],
    )
    @action(detail=True, methods=["get"])
    def watch_history(self, request, pk=None):
        child = self.get_object()
        history = child.watch_history.select_related("video").all()
        serializer = WatchHistorySerializer(
            history, many=True, context={"request": request}
        )
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Список записей истории просмотров",
        description="Возвращает историю просмотров для всех детей текущего пользователя. "
        "Поддерживает фильтрацию по ребёнку и видео.",
        parameters=[
            OpenApiParameter(
                name="child",
                type=OpenApiTypes.INT,
                description="Фильтр по ID детского профиля.",
            ),
            OpenApiParameter(
                name="video",
                type=OpenApiTypes.INT,
                description="Фильтр по ID видео.",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                description="Сортировка: `watched_at`, `watched_seconds`. "
                "По умолчанию `-watched_at`.",
            ),
        ],
        responses={200: WatchHistorySerializer(many=True)},
        tags=["Watch History"],
    ),
    create=extend_schema(
        summary="Записать просмотр",
        description="Создаёт запись о просмотре видео ребёнком. "
        "Поле `watched_at` заполняется автоматически.",
        request=WatchHistorySerializer,
        responses={
            201: WatchHistorySerializer,
            400: OpenApiResponse(description="Ошибка валидации."),
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "child": 1,
                    "video": 3,
                    "watched_seconds": 240,
                },
                request_only=True,
            )
        ],
        tags=["Watch History"],
    ),
    retrieve=extend_schema(
        summary="Получить запись просмотра",
        description="Возвращает одну запись истории просмотров по `id`.",
        responses={
            200: WatchHistorySerializer,
            404: OpenApiResponse(description="Запись не найдена."),
        },
        tags=["Watch History"],
    ),
    update=extend_schema(
        summary="Обновить запись просмотра (PUT)",
        description="Полное обновление записи просмотра.",
        request=WatchHistorySerializer,
        responses={
            200: WatchHistorySerializer,
            400: OpenApiResponse(description="Ошибка валидации."),
            404: OpenApiResponse(description="Запись не найдена."),
        },
        tags=["Watch History"],
    ),
    partial_update=extend_schema(
        summary="Обновить запись просмотра (PATCH)",
        description="Частичное обновление записи просмотра (например, досмотренные секунды).",
        request=WatchHistorySerializer,
        responses={
            200: WatchHistorySerializer,
            400: OpenApiResponse(description="Ошибка валидации."),
            404: OpenApiResponse(description="Запись не найдена."),
        },
        tags=["Watch History"],
    ),
    destroy=extend_schema(
        summary="Удалить запись просмотра",
        description="Удаляет запись из истории просмотров.",
        responses={
            204: OpenApiResponse(description="Запись удалена."),
            404: OpenApiResponse(description="Запись не найдена."),
        },
        tags=["Watch History"],
    ),
)
class WatchHistoryViewSet(viewsets.ModelViewSet):
    """Логирование и просмотр истории. Скоуп — дети текущего пользователя."""

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
