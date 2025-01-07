import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import BookmarkList, Bookmark, Place

# BookmarkList 레코드 추가
bookmarklists = [
    BookmarkList(place_id=Place.objects.get(place_id="pc_00001"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00001"), day_num=0, order=0),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00002"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00002"), day_num=0, order=0),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00003"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00003"), day_num=0, order=0),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00004"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00004"), day_num=0, order=0),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00005"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00005"), day_num=0, order=0),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00006"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00006"), day_num=1, order=1),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00007"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00006"), day_num=1, order=2),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00008"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00006"), day_num=1, order=3),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00009"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00006"), day_num=1, order=4),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00010"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00007"), day_num=2, order=1),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00011"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00007"), day_num=2, order=2),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00012"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00007"), day_num=2, order=3),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00008"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00007"), day_num=2, order=4),
    BookmarkList(place_id=Place.objects.get(place_id="pc_00013"), bookmark_id=Bookmark.objects.get(bookmark_id="bm_00007"), day_num=2, order=5),
]

BookmarkList.objects.bulk_create(bookmarklists)

print("BookmarkList 데이터 추가 완료!")
