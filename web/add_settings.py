import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import Settings, CustomUser, Country

# Settings 레코드 추가
settings = [
    Settings(profile_id=CustomUser.objects.get(username="user1"), country_id=Country.objects.get(country_id="CN"), is_white_theme=True),
    Settings(profile_id=CustomUser.objects.get(username="user2"), country_id=Country.objects.get(country_id="US"), is_white_theme=False),
    Settings(profile_id=CustomUser.objects.get(username="user3"), country_id=Country.objects.get(country_id="JP"), is_white_theme=True),
]

Settings.objects.bulk_create(settings)

print("Settings 데이터 추가 완료!")
