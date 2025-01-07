import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import Settings, CustomUser, Country

# Settings 레코드 추가
settings = [
    {
        "profile": CustomUser.objects.get(username="user1").id,
        "country": Country.objects.get(country_id="CN").country_id,
        "is_white_theme": True,
    },
    {
        "profile": CustomUser.objects.get(username="user2").id,
        "country": Country.objects.get(country_id="US").country_id,
        "is_white_theme": False,
    },
    {
        "profile": CustomUser.objects.get(username="user3").id,
        "country": Country.objects.get(country_id="JP").country_id,
        "is_white_theme": True,
    },
]

# Create Settings instances
settings_instances = [
    Settings(
        profile_id=setting["profile"],
        country_id=setting["country"],
        is_white_theme=setting["is_white_theme"],
    )
    for setting in settings
]

# Bulk create the settings
Settings.objects.bulk_create(settings_instances)

print("Settings 데이터 추가 완료!")
