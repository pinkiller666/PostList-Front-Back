from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand


class Command(RunserverCommand):
    # порт, уникальный для этого проекта
    default_port = "8081"