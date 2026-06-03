from django.db import models
from django.db.models import Q, CheckConstraint
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone


def current_order_month():
    return timezone.localdate().strftime("%Y-%m")


class ArtStatus(models.TextChoices):
    DONE = "done", "Готово"
    IN_PROGRESS = "in_progress", "В процессе"
    CANCELLED = "cancelled", "Отменено"
    ONLY_PLANNED = "only_planned", "Только запланировано"
    WAITING_TO_START = "waiting_to_start", "Ожидает начала"
    DELETED = "deleted", "Удалено"


class IsFurry(models.TextChoices):
    YES = "yes", "Фурри"
    NO = "no", "Не фурри"


class IsHuman(models.TextChoices):
    YES = "yes", "Человек"
    NO = "no", "Не человек"


class HowLewd(models.TextChoices):
    ONLY_LEWD = "only_lewd", "Только NSFW"
    ONLY_DECENT = "only_decent", "Только SFW"
    BOTH = "both", "Обе версии"
    LEWD_WITH_SFW_VARIANT = "lewd_with_sfw_variant", "NSFW + SFW-кроп/спойлер"


class PostState(models.TextChoices):
    NOT_POSTED = "not_posted", "Не выложено"
    SCHEDULED = "scheduled", "Запланировано"
    POSTED = "posted", "Выложено"


class PaymentStatus(models.TextChoices):
    UNPAID = "unpaid", "Не оплачена"
    PARTIALLY_PAID = "partially_paid", "Частично оплачена"
    FULLY_PAID = "fully_paid", "Фул оплачена"
    HALF_BEFORE_SKETCH = "half_before_sketch", "Половина до скетча"


class PayoutStatus(models.TextChoices):
    NOT_WITHDRAWN = "not_withdrawn", "Не выведено"
    PARTIALLY_WITHDRAWN = "partially_withdrawn", "Частично выведено"
    WITHDRAWN = "withdrawn", "Выведено"


class Art(models.Model):
    name = models.CharField(max_length=200)

    status = models.CharField(
        max_length=32,
        choices=ArtStatus.choices,
        default=ArtStatus.ONLY_PLANNED,
        db_index=True,
    )

    locked = models.BooleanField(default=False)

    order_month = models.CharField(
        max_length=7,
        default=current_order_month,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r"^\d{4}-(0[1-9]|1[0-2])$",
                message="Месяц заказа должен быть в формате YYYY-MM.",
            ),
        ],
        help_text="Месяц заказа в формате YYYY-MM.",
    )

    # На будущее лучше DecimalField(max_digits=10, decimal_places=2)
    price = models.IntegerField(default=0)

    payment_status = models.CharField(
        max_length=32,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        db_index=True,
    )

    is_fanart = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Фанарт / личная работа без финансового блока.",
    )

    payout_status = models.CharField(
        max_length=32,
        choices=PayoutStatus.choices,
        default=PayoutStatus.NOT_WITHDRAWN,
        db_index=True,
    )

    furry_type = models.CharField(
        max_length=32,
        choices=IsFurry.choices,
        default=IsFurry.NO,
    )

    human_type = models.CharField(
        max_length=32,
        choices=IsHuman.choices,
        default=IsHuman.YES,
    )

    is_nsfw = models.BooleanField(default=False)
    is_sfw = models.BooleanField(default=False)
    is_nsfw_plus_crop = models.BooleanField(default=False)

    # куда планируем постить
    post_on_bsky = models.BooleanField(default=False)
    post_on_lewd_twi = models.BooleanField(default=False)
    post_on_decent_twi = models.BooleanField(default=False)

    # статусы по площадкам
    bsky_posted = models.CharField(
        max_length=12,
        choices=PostState.choices,
        default=PostState.NOT_POSTED,
    )
    lewd_twi_posted = models.CharField(
        max_length=12,
        choices=PostState.choices,
        default=PostState.NOT_POSTED,
    )
    decent_twi_posted = models.CharField(
        max_length=12,
        choices=PostState.choices,
        default=PostState.NOT_POSTED,
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-order_month", "-created_at")

        # DB-уровень: не даём сохранить невозможные комбинации даже при прямой работе с моделью
        constraints = [
            # Нельзя одновременно иметь полноценную SFW и режим "NSFW + crop"
            CheckConstraint(
                check=~(
                        Q(is_nsfw_plus_crop=True) &
                        Q(is_sfw=True)
                ),
                name="art_no_sfw_with_nsfw_plus_crop",
            ),
            # "NSFW + crop" требует существования полноценной NSFW-версии
            CheckConstraint(
                check=~(
                        Q(is_nsfw_plus_crop=True) &
                        Q(is_nsfw=False)
                ),
                name="art_nsfw_plus_crop_requires_nsfw",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if self.is_nsfw_plus_crop and self.is_sfw:
            msg = (
                "Нельзя одновременно иметь полноценную SFW-версию "
                "и режим «NSFW + crop» — либо нормальная SFW, либо только кроп."
            )
            errors["is_sfw"] = msg
            errors["is_nsfw_plus_crop"] = msg

        if self.is_nsfw_plus_crop and not self.is_nsfw:
            msg = (
                "Режим «NSFW + crop» возможен только если есть полноценная "
                "NSFW-версия (is_nsfw=True)."
            )
            errors["is_nsfw"] = msg
            errors["is_nsfw_plus_crop"] = msg

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return str(self.name)

class PaymentPartStatus(models.TextChoices):
    EXPECTED = "expected", "Ожидается"
    RECEIVED = "received", "Получено у посредника"
    WITHDRAWN = "withdrawn", "Выведено"


class PaymentPart(models.Model):
    art = models.ForeignKey(
        Art,
        related_name="payment_parts",
        on_delete=models.CASCADE,
    )

    amount_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=32,
        choices=PaymentPartStatus.choices,
        default=PaymentPartStatus.EXPECTED,
        db_index=True,
    )

    note = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.art.name}: ${self.amount_usd} ({self.status})"


class Payout(models.Model):
    order_month = models.CharField(
        max_length=7,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r"^\d{4}-(0[1-9]|1[0-2])$",
                message="Месяц вывода должен быть в формате YYYY-MM.",
            ),
        ],
    )

    date = models.DateField(default=timezone.localdate)

    amount_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    amount_rub = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    comment = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def exchange_rate(self):
        if not self.amount_usd:
            return 0
        return self.amount_rub / self.amount_usd

    def __str__(self):
        return f"{self.order_month}: ${self.amount_usd} → ₽{self.amount_rub}"


class PayoutAllocation(models.Model):
    payout = models.ForeignKey(
        Payout,
        related_name="allocations",
        on_delete=models.CASCADE,
    )

    payment_part = models.ForeignKey(
        PaymentPart,
        related_name="payout_allocations",
        on_delete=models.PROTECT,
    )

    amount_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_part.art.name}: ${self.amount_usd} in payout #{self.payout_id}"

