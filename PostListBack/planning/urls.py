from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DraftMonthDayOverrideViewSet,
    DraftMonthScheduleViewSet,
)

router = DefaultRouter()

router.register(
    'draft-month-schedules',
    DraftMonthScheduleViewSet,
    basename='draft-month-schedule',
)

router.register(
    'draft-month-day-overrides',
    DraftMonthDayOverrideViewSet,
    basename='draft-month-day-override',
)

urlpatterns = [
    path('', include(router.urls)),
]