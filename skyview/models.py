from django.db import models
from django.utils.text import slugify


class Place(models.Model):
    name = models.CharField(max_length=100, unique=True)
    priority = models.PositiveSmallIntegerField(null=True, blank=True)
    intro_url = models.URLField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["priority", "name"]

    def __str__(self):
        return self.name

    @property
    def slug(self):
        return slugify(self.name, allow_unicode=True)


class Video(models.Model):
    VIDEO_TYPE_LANDSCAPE = "L"
    VIDEO_TYPE_SHORTS = "S"
    VIDEO_TYPE_CHOICES = [
        (VIDEO_TYPE_LANDSCAPE, "Landscape 16:9"),
        (VIDEO_TYPE_SHORTS, "Shorts 9:16"),
    ]

    place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="videos",
    )
    title = models.CharField(max_length=200)
    youtube_url = models.URLField()
    youtube_id = models.CharField(max_length=20, blank=True)
    video_type = models.CharField(max_length=1, choices=VIDEO_TYPE_CHOICES)
    published_date = models.DateField(null=True, blank=True)
    display_rank = models.PositiveSmallIntegerField(null=True, blank=True)
    insight_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-published_date", "title"]

    def __str__(self):
        return self.title

    @property
    def thumbnail_url(self):
        if self.youtube_id:
            return f"https://img.youtube.com/vi/{self.youtube_id}/mqdefault.jpg"
        return ""

    @property
    def short_description(self):
        if self.place:
            return self.place.name
        return ""


class FamilySite(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    description = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title
