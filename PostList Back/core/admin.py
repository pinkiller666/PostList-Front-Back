from django.contrib import admin
from .models import Art


@admin.register(Art)
class ArtAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "status", "how_lewd",
        "human_type", "furry_type",
        "post_on_bsky", "post_on_decent_twi", "post_on_lewd_twi",
        "bsky_posted", "decent_twi_posted", "lewd_twi_posted",
        "created_at",
    )
    list_filter = (
        "status", "how_lewd", "human_type", "furry_type",
        "bsky_posted", "decent_twi_posted", "lewd_twi_posted",
        "post_on_bsky", "post_on_decent_twi", "post_on_lewd_twi",
        "created_at",
    )
    search_fields = ("name",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
