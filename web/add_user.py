import os
import django
from django.contrib.auth.hashers import make_password

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import CustomUser, Country

users = [
    {"username": "user1", "password": "password1", "email": "user1@example.com", "country_id": "KR"},
    {"username": "user2", "password": "password2", "email": "user2@example.com", "country_id": "US"},
    {"username": "user3", "password": "password3", "email": "user3@example.com", "country_id": "JP"},
]

for user_data in users:
    # country_id를 문자열로 할당
    CustomUser.objects.update_or_create(
        username=user_data["username"],
        defaults={
            "password": user_data["password"],
            "email": user_data["email"],
            "country_id": user_data["country_id"],  # Country 객체 대신 PK 값 전달
        },
    )

print("사용자 데이터 추가 또는 업데이트 완료!")

