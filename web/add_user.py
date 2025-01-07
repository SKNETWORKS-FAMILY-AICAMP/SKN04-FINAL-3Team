import os
import django
from django.contrib.auth.hashers import make_password

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import CustomUser, Country

users = [
    {"username": "user1", "password": "pbkdf2_sha256$870000$wV43cxWfYHBeXIuvhUf3B7$Vl31ukoNg65jTcXRSTWZWLzulSLwMXPTvCvzQ312+NM=", "email": "user1@example.com", "country_id": "KR", "birthday": "2004-12-22", "thumbnail_id": 1, "nickname": "서울깍쟁이"},
    {"username": "user2", "password": "pbkdf2_sha256$870000$wV43cxWfYHBeXIuvhUf3B7$Vl31ukoNg65jTcXRSTWZWLzulSLwMXPTvCvzQ312+NM=", "email": "user2@example.com", "country_id": "US", "birthday": "1997-05-14", "thumbnail_id": 1, "nickname": "kate"},
    {"username": "user3", "password": "pbkdf2_sha256$870000$wV43cxWfYHBeXIuvhUf3B7$Vl31ukoNg65jTcXRSTWZWLzulSLwMXPTvCvzQ312+NM=", "email": "user3@example.com", "country_id": "JP", "birthday": "1999-02-01", "thumbnail_id": 1, "nickname": "富士山"},
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

