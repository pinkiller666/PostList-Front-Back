from django.contrib import admin
from .models import Art, ExternalIncomePayoutAllocation, PaymentPart, Payout, PayoutAllocation, ExternalIncome


@admin.register(Art)
class ArtAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "locked",
        "status",
        "order_month",
        "is_fanart",
        "price",
        "payment_status",
        "payout_status",
        "is_sfw",
        "is_nsfw",
        "is_nsfw_plus_crop",
        "human_type",
        "furry_type",
        "post_on_bsky",
        "post_on_decent_twi",
        "post_on_lewd_twi",
        "bsky_posted",
        "decent_twi_posted",
        "lewd_twi_posted",
        "created_at",
    )

    list_filter = (
        "status",
        "order_month",
        "is_fanart",
        "payment_status",
        "payout_status",
        "human_type",
        "furry_type",
        "is_sfw",
        "is_nsfw",
        "is_nsfw_plus_crop",
        "bsky_posted",
        "decent_twi_posted",
        "lewd_twi_posted",
        "post_on_bsky",
        "post_on_decent_twi",
        "post_on_lewd_twi",
        "locked",
        "created_at",
    )

    search_fields = ("name",)
    ordering = ("-order_month", "-created_at")
    date_hierarchy = "created_at"

    fieldsets = (
        ("Основное", {
            "fields": (
                "name",
                "status",
                "human_type",
                "furry_type",
                "order_month",
                "is_fanart",
                "price",
                "payment_status",
                "payout_status",
                "locked",
            )
        }),
        ("Контент (SFW/NSFW)", {
            "fields": (
                "is_sfw",
                "is_nsfw",
                "is_nsfw_plus_crop",
            )
        }),
        ("Постинг", {
            "fields": (
                "post_on_bsky",
                "post_on_decent_twi",
                "post_on_lewd_twi",
                "bsky_posted",
                "decent_twi_posted",
                "lewd_twi_posted",
            )
        }),
    )

@admin.register(PaymentPart)
class PaymentPartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "art",
        "amount_usd",
        "status",
        "note",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "art__name",
        "note",
    )

    autocomplete_fields = (
        "art",
    )

    ordering = ("-created_at",)


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_month",
        "date",
        "amount_usd",
        "amount_rub",
        "exchange_rate",
        "comment",
        "created_at",
    )

    list_filter = (
        "order_month",
        "date",
        "created_at",
    )

    search_fields = (
        "comment",
    )

    ordering = ("-date", "-created_at")


@admin.register(PayoutAllocation)
class PayoutAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payout",
        "payment_part",
        "amount_usd",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "payment_part__art__name",
    )

    autocomplete_fields = (
        "payout",
        "payment_part",
    )

    ordering = ("-created_at",)

@admin.register(ExternalIncome)
class ExternalIncomeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_month",
        "source",
        "amount_usd",
        "note",
        "created_at",
    )

    list_filter = (
        "order_month",
        "source",
        "created_at",
    )

    search_fields = (
        "note",
    )

    ordering = ("-order_month", "-created_at")

@admin.register(ExternalIncomePayoutAllocation)
class ExternalIncomePayoutAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payout",
        "external_income",
        "amount_usd",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "external_income__note",
        "external_income__source",
    )

    autocomplete_fields = (
        "payout",
        "external_income",
    )

    ordering = ("-created_at",)