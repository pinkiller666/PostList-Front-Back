from rest_framework import viewsets

from .models import DraftMonthDayOverride, DraftMonthSchedule
from .serializers import (
    DraftMonthDayOverrideSerializer,
    DraftMonthScheduleSerializer,
)


class DraftMonthScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = DraftMonthScheduleSerializer

    def get_queryset(self):
        return DraftMonthSchedule.objects.prefetch_related(
            'day_overrides',
        )


class DraftMonthDayOverrideViewSet(viewsets.ModelViewSet):
    serializer_class = DraftMonthDayOverrideSerializer

    def get_queryset(self):
        queryset = DraftMonthDayOverride.objects.select_related('schedule')

        schedule_id = self.request.query_params.get('schedule')

        if schedule_id:
            queryset = queryset.filter(schedule_id=schedule_id)

        return queryset