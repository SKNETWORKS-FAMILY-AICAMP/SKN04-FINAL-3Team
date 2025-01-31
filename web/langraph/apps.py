# langraph/apps.py
from django.apps import AppConfig

class LangraphConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'langraph'  # 앱 이름은 디렉토리 이름과 동일해야 합니다.
