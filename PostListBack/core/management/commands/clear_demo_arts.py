from django.core.management.base import BaseCommand
from core.models import Art

DEMO_PREFIX = "demo_"


class Command(BaseCommand):
    help = "Удаляет все демо-арты, у которых name начинается с 'demo_'."

    def handle(self, *args, **options):
        qs = Art.objects.filter(name__startswith=DEMO_PREFIX)
        count = qs.count()
        qs.delete()

        self.stdout.write(
            self.style.WARNING(f"Удалено демо-артов: {count}")
        )
