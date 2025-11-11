from django.core.management.commands.runserver import Command as RunserverCommand


class Command(RunserverCommand):
    # укажи порт, уникальный для ЭТОГО проекта
    default_port = "8081"
