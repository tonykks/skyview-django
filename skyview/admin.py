from django.contrib import admin

from .models import FamilySite, Place, Video


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "priority", "latitude", "longitude", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "place",
        "video_type",
        "published_date",
        "display_rank",
        "is_active",
    )
    list_display_links = ("id",)
    list_editable = ("title",)
    list_filter = ("video_type", "place", "is_active", "display_rank")
    search_fields = ("title", "youtube_url", "youtube_id", "insight_url")
    ordering = ("-published_date",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "place",
                    "video_type",
                    "published_date",
                    "display_rank",
                    "is_active",
                ),
            },
        ),
        (
            "YouTube",
            {
                "fields": ("youtube_url", "youtube_id", "insight_url"),
            },
        ),
    )


@admin.register(FamilySite)
class FamilySiteAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    ordering = ("order",)
