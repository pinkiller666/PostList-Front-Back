from django.db import models


class ArtStatus(models.TextChoices):
    DONE = "done", "Готово"
    IN_PROGRESS = "in_progress", "В процессе"
    CANCELLED = "cancelled", "Отменено"
    ONLY_PLANNED = "only_planned", "Только запланировано"
    WAITING_TO_START = "waiting_to_start", "Ожидает начала"


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


class WhereToPost(models.TextChoices):
    BLSKY = "blsky", "Bluesky"
    TWI_16 = "twi16", "Твиттер 16+"
    TWI_18 = "twi18", "Твиттер 18+"


class PostState(models.TextChoices):
    NOT_POSTED = "not_posted", "Не выложено"
    SCHEDULED = "scheduled", "Запланировано"
    POSTED = "posted", "Выложено"


class Art(models.Model):
    name = models.CharField(max_length=200)

    status = models.CharField(
        max_length=32,
        choices=ArtStatus.choices,
        default=ArtStatus.ONLY_PLANNED,
        db_index=True,
    )

    # На будущее лучше DecimalField(max_digits=10, decimal_places=2)
    price = models.IntegerField(default=0)

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

    how_lewd = models.CharField(
        max_length=32,
        choices=HowLewd.choices,
        default=HowLewd.ONLY_DECENT,
    )

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
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return str(self.name)
