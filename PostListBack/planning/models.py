from calendar import monthrange
from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class DraftDayType(models.TextChoices):
    WORK = 'work', 'Рабочий'
    OFF = 'off', 'Выходной'
    PLANNING = 'planning', 'Планирование'
    CANCELLED = 'cancelled', 'Отменён'
    MOVED = 'moved', 'Перенесён'


class DraftMonthSchedule(models.Model):
    year = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(2100),
        ],
    )

    month = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ],
    )

    days_off_at_start = models.PositiveSmallIntegerField(default=4)

    cycle_work_days = models.PositiveSmallIntegerField(default=2)
    cycle_off_days = models.PositiveSmallIntegerField(default=2)

    last_day_is_working = models.BooleanField(default=True)
    first_working_day_is_planning = models.BooleanField(default=True)

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month']
        constraints = [
            models.UniqueConstraint(
                fields=['year', 'month'],
                name='unique_draft_schedule_month',
            ),
        ]

    def __str__(self):
        return f'Черновое расписание: {self.month:02}.{self.year}'

    def clean(self):
        if self.cycle_work_days == 0 and self.cycle_off_days == 0:
            raise ValidationError(
                'В цикле должен быть хотя бы один рабочий или выходной день.'
            )

    def generate_days(self):
        days_count = monthrange(self.year, self.month)[1]
        days = []

        for day_number in range(1, days_count + 1):
            current_date = date(self.year, self.month, day_number)
            day_type = self._get_base_day_type(day_number, days_count)

            days.append({
                'date': current_date.isoformat(),
                'day_number': day_number,
                'day_type': day_type,
                'comment': '',
                'moved_to_date': None,
            })

        self._apply_overrides(days)
        self._mark_first_working_day_as_planning(days)

        return days

    def _get_base_day_type(self, day_number, days_count):
        if day_number <= self.days_off_at_start:
            return DraftDayType.OFF

        cycle_length = self.cycle_work_days + self.cycle_off_days
        cycle_index = day_number - self.days_off_at_start - 1
        position_in_cycle = cycle_index % cycle_length

        if position_in_cycle < self.cycle_work_days:
            day_type = DraftDayType.WORK
        else:
            day_type = DraftDayType.OFF

        if day_number == days_count and self.last_day_is_working:
            day_type = DraftDayType.WORK

        return day_type

    def _apply_overrides(self, days):
        overrides_by_date = {
            override.date.isoformat(): override
            for override in self.day_overrides.all()
        }

        for day in days:
            override = overrides_by_date.get(day['date'])

            if not override:
                continue

            day['day_type'] = override.day_type
            day['comment'] = override.comment

            if override.moved_to_date:
                day['moved_to_date'] = override.moved_to_date.isoformat()

    def _mark_first_working_day_as_planning(self, days):
        if not self.first_working_day_is_planning:
            return

        has_manual_planning_day = any(
            day['day_type'] == DraftDayType.PLANNING
            for day in days
        )

        if has_manual_planning_day:
            return

        for day in days:
            if day['day_type'] == DraftDayType.WORK:
                day['day_type'] = DraftDayType.PLANNING
                return


class DraftMonthDayOverride(models.Model):
    schedule = models.ForeignKey(
        DraftMonthSchedule,
        on_delete=models.CASCADE,
        related_name='day_overrides',
    )

    date = models.DateField()

    day_type = models.CharField(
        max_length=20,
        choices=DraftDayType.choices,
    )

    moved_to_date = models.DateField(
        null=True,
        blank=True,
    )

    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['date']
        constraints = [
            models.UniqueConstraint(
                fields=['schedule', 'date'],
                name='unique_draft_schedule_day_override',
            ),
        ]

    def __str__(self):
        return f'{self.date}: {self.get_day_type_display()}'

    def clean(self):
        if self.date.year != self.schedule.year:
            raise ValidationError('Дата должна быть внутри года расписания.')

        if self.date.month != self.schedule.month:
            raise ValidationError('Дата должна быть внутри месяца расписания.')

        if self.day_type == DraftDayType.MOVED and not self.moved_to_date:
            raise ValidationError(
                'Для перенесённого дня нужно указать дату переноса.'
            )