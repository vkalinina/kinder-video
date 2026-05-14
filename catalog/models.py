from django.db import models
from django.conf import settings
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    """
    Abstract base model that adds creation and update timestamps.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """
    Video category owned by a specific user.
    Each parent has their own private set of categories.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    # UI customization
    color = models.CharField(
        max_length=7,
        default="#4F46E5",
        help_text="The color of the category. HEX color code, e.g. #4F46E5",
    )
    icon = models.ImageField(
        max_length=50,
        blank=True,
        help_text="Optional icon name, e.g. 'book', 'music', 'star'",
    )

    # Sorting and visibility
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        unique_together = ["owner", "slug"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Video(TimeStampedModel):
    """
    YouTube video added by a specific user.
    Displayed inside the application using youtube-nocookie.com
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="videos",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="videos",
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    # YouTube data
    youtube_url = models.URLField()
    youtube_id = models.CharField(
        max_length=20,
        help_text="Example: dQw4w9WgXcQ",
    )

    # Thumbnail
    thumbnail = models.ImageField(
        upload_to="video_thumbnail/",
        blank=True,
        null=True,
    )

    # Sorting and status
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Optional metadata
    duration_seconds = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["order", "title"]
        unique_together = ["owner", "youtube_id"]
        verbose_name = "Video"
        verbose_name_plural = "Videos"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def embed_url(self):
        return f"https://youtube-nocookie.com/embed/" f"{self.youtube_id}?rel=0"

    def __str__(self):
        return self.title


class ChildProfile(TimeStampedModel):
    """
    Child profile linked to a parent account.
    Can be used for PIN protection and viewing limits.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="children",
    )
    name = models.CharField(max_length=255)

    # Optional PIN code for child login
    pin_code = models.CharField(
        max_length=10,
        blank=True,
    )

    # Daily viewing limit in minutes
    daily_limit_minutes = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Child Profile"
        verbose_name_plural = "Child Profiles"

    def __str__(self):
        return self.name


class WatchHistory(TimeStampedModel):
    """
    Stores information about which child watched which video.
    """

    child = models.ForeignKey(
        ChildProfile, on_delete=models.CASCADE, related_name="watch_history"
    )
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="watch_history"
    )

    watched_at = models.DateTimeField(auto_now_add=True)
    watched_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-watched_at"]
        verbose_name = "Watch History"
        verbose_name_plural = "Watch Histories"

    def __str__(self):
        return f"{self.child.name} watched {self.video.title}"
