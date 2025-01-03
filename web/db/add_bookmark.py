import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import Bookmark, CustomUser

# Bookmark 레코드 추가
bookmarks = [
    Bookmark(bookmark_id="bm_00001", profile_id=CustomUser.objects.get(username="user1"), title="서울 명소 즐겨찾기", is_place=True),
    Bookmark(bookmark_id="bm_00002", profile_id=CustomUser.objects.get(username="user2"), title="뉴욕 명소 즐겨찾기", is_place=True),
    Bookmark(bookmark_id="bm_00003", profile_id=CustomUser.objects.get(username="user3"), title="도쿄 명소 즐겨찾기", is_place=True),
]

Bookmark.objects.bulk_create(bookmarks)

print("Bookmark 데이터 추가 완료!")
