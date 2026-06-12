from rest_framework import serializers

from .models import DraftMonthDayOverride, DraftMonthSchedule


class DraftMonthDayOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftMonthDayOverride
        fields = [
            'id',
            'schedule',
            'date',
            'day_type',
            'moved_to_date',
            'comment',
        ]

    def validate(self, attrs):
        schedule = attrs.get('schedule') or self.instance.schedule
        override_date = attrs.get('date') or self.instance.date

        if override_date.year != schedule.year:
            raise serializers.ValidationError(
                'Дата должна быть внутри года расписания.'
            )

        if override_date.month != schedule.month:
            raise serializers.ValidationError(
                'Дата должна быть внутри месяца расписания.'
            )

        return attrs


class DraftMonthScheduleSerializer(serializers.ModelSerializer):
    day_overrides = DraftMonthDayOverrideSerializer(
        many=True,
        read_only=True,
    )

    generated_days = serializers.SerializerMethodField()

    class Meta:
        model = DraftMonthSchedule
        fields = [
            'id',
            'year',
            'month',
            'days_off_at_start',
            'cycle_work_days',
            'cycle_off_days',
            'last_day_is_working',
            'first_working_day_is_planning',
            'comment',
            'day_overrides',
            'generated_days',
            'created_at',
            'updated_at',
        ]

    def get_generated_days(self, obj):
        return obj.generate_days()