import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import BookmarkList, Bookmark, Place

# BookmarkList 레코드 추가
bookmarklists = [
    {"place_id": "pc_00001", "bookmark_id": "bm_00001", "day_num": 0, "order": 0},
    {"place_id": "pc_00002", "bookmark_id": "bm_00002", "day_num": 0, "order": 0},
    {"place_id": "pc_00003", "bookmark_id": "bm_00003", "day_num": 0, "order": 0},
    {"place_id": "pc_00004", "bookmark_id": "bm_00004", "day_num": 0, "order": 0},
    {"place_id": "pc_00005", "bookmark_id": "bm_00005", "day_num": 0, "order": 0},
    {"place_id": "pc_00006", "bookmark_id": "bm_00006", "day_num": 1, "order": 1},
    {"place_id": "pc_00007", "bookmark_id": "bm_00006", "day_num": 1, "order": 2},
    {"place_id": "pc_00008", "bookmark_id": "bm_00006", "day_num": 1, "order": 3},
    {"place_id": "pc_00009", "bookmark_id": "bm_00006", "day_num": 1, "order": 4},
    {"place_id": "pc_00010", "bookmark_id": "bm_00007", "day_num": 2, "order": 1},
    {"place_id": "pc_00011", "bookmark_id": "bm_00007", "day_num": 2, "order": 2},
    {"place_id": "pc_00012", "bookmark_id": "bm_00007", "day_num": 2, "order": 3},
    {"place_id": "pc_00008", "bookmark_id": "bm_00007", "day_num": 2, "order": 4},
    {"place_id": "pc_00013", "bookmark_id": "bm_00007", "day_num": 2, "order": 5},
]

try:
    # 중복되지 않은 데이터만 삽입
    new_bookmarklists = []
    for data in bookmarklists:
        place = Place.objects.get(place_id=data["place_id"])
        bookmark = Bookmark.objects.get(bookmark=data["bookmark_id"])
        
        # 중복 여부 확인
        if not BookmarkList.objects.filter(place=place, bookmark=bookmark, day_num=data["day_num"], order=data["order"]).exists():
            new_bookmarklists.append(
                BookmarkList(
                    place=place,
                    bookmark=bookmark,
                    day_num=data["day_num"],
                    order=data["order"],
                )
            )
except Bookmark.DoesNotExist:
    print(f"Bookmark with ID {data['bookmark_id']} does not exist.")

# 새로운 데이터만 bulk_create
if new_bookmarklists:
    BookmarkList.objects.bulk_create(new_bookmarklists)
    print(f"{len(new_bookmarklists)}개의 BookmarkList 데이터가 추가되었습니다!")
else:
    print("중복 데이터가 존재하여 추가된 데이터가 없습니다.")
