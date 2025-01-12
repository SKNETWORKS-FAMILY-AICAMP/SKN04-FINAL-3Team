# langgraph/apps.py
from django.apps import AppConfig

class LanggraphConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web.langgraph'  # Django에서 사용하는 경로
