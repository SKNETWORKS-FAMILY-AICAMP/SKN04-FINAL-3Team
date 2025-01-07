import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import Bookmark, CustomUser

# Bookmark 레코드 추가
bookmarks = [
    {"bookmark": "bm_00001", "username": "user1", "title": "국립중앙박물관", "is_place": True},
    {"bookmark": "bm_00002", "username": "user2", "title": "이태원", "is_place": True},
    {"bookmark": "bm_00003", "username": "user3", "title": "남산스", "is_place": True},
    {"bookmark": "bm_00004", "username": "user1", "title": "용산 전자 상가", "is_place": True},
    {"bookmark": "bm_00005", "username": "user1", "title": "한강", "is_place": True},
    {"bookmark": "bm_00006", "username": "user1", "title": "용산 투어", "is_place": False},
    {"bookmark": "bm_00007", "username": "user1", "title": "명동 일정", "is_place": False},
    {"bookmark": "bm_00008", "username": "user1", "title": "서울", "is_place": False},
    {"bookmark": "bm_00009", "username": "user1", "title": "종로구", "is_place": False},
]

for data in bookmarks:
    if not Bookmark.objects.filter(bookmark=data["bookmark"]).exists():
        profile = CustomUser.objects.get(username=data["username"])
        Bookmark.objects.create(
            bookmark=data["bookmark"],
            profile=profile,
            title=data["title"],
            is_place=data["is_place"]
        )
    else:
        print(f'Bookmark with id {data["bookmark"]} already exists.')

print("Bookmark 데이터 추가 완료!")
