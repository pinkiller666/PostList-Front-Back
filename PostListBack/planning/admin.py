from django.contrib import admin

from .models import DraftMonthDayOverride, DraftMonthSchedule


class DraftMonthDayOverrideInline(admin.TabularInline):
    model = DraftMonthDayOverride
    extra = 0
    fields = [
        'date',
        'day_type',
        'moved_to_date',
        'comment',
    ]


@admin.register(DraftMonthSchedule)
class DraftMonthScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'year',
        'month',
        'days_off_at_start',
        'cycle_work_days',
        'cycle_off_days',
        'last_day_is_working',
        'first_working_day_is_planning',
    ]

    list_filter = [
        'year',
        'month',
        'last_day_is_working',
        'first_working_day_is_planning',
    ]

    inlines = [
        DraftMonthDayOverrideInline,
    ]


@admin.register(DraftMonthDayOverride)
class DraftMonthDayOverrideAdmin(admin.ModelAdmin):
    list_display = [
        'schedule',
        'date',
        'day_type',
        'moved_to_date',
        'comment',
    ]

    list_filter = [
        'day_type',
        'date',
    ]

    search_fields = [
        'comment',
    ]