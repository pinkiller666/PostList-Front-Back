import random
from django.core.management.base import BaseCommand
from core.models import Art, ArtStatus, IsHuman, IsFurry, PostState


DEMO_PREFIX = "demo_"


class Command(BaseCommand):
    help = "Создаёт пачку демо-артов с префиксом 'demo_' в имени."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Сколько демо-артов создать (по умолчанию 5)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        created = 0

        for idx in range(count):
            # Немного разнообразных тайтлов
            name = f"{DEMO_PREFIX}арт_{idx+1}"

            # Статус
            status = random.choice([
                ArtStatus.ONLY_PLANNED,
                ArtStatus.IN_PROGRESS,
                ArtStatus.DONE,
                ArtStatus.CANCELLED,
                ArtStatus.WAITING_TO_START,
            ])

            # Человек / фурри
            human_type = random.choice([IsHuman.YES, IsHuman.NO])
            furry_type = random.choice([IsFurry.YES, IsFurry.NO])

            # Цена (временно рандом)
            price = random.choice([0, 50, 100, 150, 200, 300])

            # Сценарий по SFW/NSFW:
            # 0: только SFW
            # 1: только NSFW
            # 2: обе версии
            # 3: NSFW + только crop
            mode = random.choice([0, 1, 2, 3])

            is_sfw = False
            is_nsfw = False
            is_nsfw_plus_crop = False

            if mode == 0:
                # только SFW
                is_sfw = True
            elif mode == 1:
                # только NSFW
                is_nsfw = True
            elif mode == 2:
                # обе полноценные версии
                is_sfw = True
                is_nsfw = True
            elif mode == 3:
                # NSFW + crop вместо SFW
                is_nsfw = True
                is_nsfw_plus_crop = True

            # Куда планируем постить
            post_on_bsky = random.choice([True, False])
            post_on_decent_twi = random.choice([True, False])
            post_on_lewd_twi = random.choice([True, False])

            # Статусы по площадкам
            post_state_choices = [
                PostState.NOT_POSTED,
                PostState.SCHEDULED,
                PostState.POSTED,
            ]

            bsky_posted = random.choice(post_state_choices)
            decent_twi_posted = random.choice(post_state_choices)
            lewd_twi_posted = random.choice(post_state_choices)

            Art.objects.create(
                name=name,
                status=status,
                locked=random.choice([True, False]),
                price=price,
                human_type=human_type,
                furry_type=furry_type,
                is_sfw=is_sfw,
                is_nsfw=is_nsfw,
                is_nsfw_plus_crop=is_nsfw_plus_crop,
                post_on_bsky=post_on_bsky,
                post_on_decent_twi=post_on_decent_twi,
                post_on_lewd_twi=post_on_lewd_twi,
                bsky_posted=bsky_posted,
                decent_twi_posted=decent_twi_posted,
                lewd_twi_posted=lewd_twi_posted,
            )

            created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Создано демо-артов: {created}")
        )
