import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import CustomUser

# CustomUser 레코드 추가
users = [
    CustomUser(username="user1", country_id="KR", birthday="1990-01-01", nickname="서울유저1", thumbnail_id=1),
    CustomUser(username="user2", country_id="US", birthday="1995-05-05", nickname="뉴욕유저", thumbnail_id=2),
    CustomUser(username="user3", country_id="JP", birthday="1988-12-12", nickname="도쿄유저", thumbnail_id=3),
]

CustomUser.objects.bulk_create(users)

print("CustomUser 데이터 추가 완료!")
