from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"

    # def ready(self):
    #     import main.signals  # signals.py 파일을 import