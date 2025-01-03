import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import Bookmark, CustomUser

# Bookmark 레코드 추가
bookmarks = [
    {"bookmark_id": "bm_00001", "username": "user1", "title": "서울 명소 즐겨찾기", "is_place": True},
    {"bookmark_id": "bm_00002", "username": "user2", "title": "뉴욕 명소 즐겨찾기", "is_place": True},
    {"bookmark_id": "bm_00003", "username": "user3", "title": "도쿄 명소 즐겨찾기", "is_place": True},
]

for data in bookmarks:
    if not Bookmark.objects.filter(bookmark_id=data["bookmark_id"]).exists():
        profile = CustomUser.objects.get(username=data["username"])
        Bookmark.objects.create(
            bookmark_id=data["bookmark_id"],
            profile_id=profile,
            title=data["title"],
            is_place=data["is_place"]
        )
    else:
        print(f'Bookmark with id {data["bookmark_id"]} already exists.')

print("Bookmark 데이터 추가 완료!")
