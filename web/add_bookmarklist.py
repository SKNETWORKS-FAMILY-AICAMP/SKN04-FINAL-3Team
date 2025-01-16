import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import BookmarkList, Bookmark, Place, Schedule

# BookmarkList 레코드 추가
bookmarklists = [
    {"schedule_id": "", "place_id": "pc_00001", "bookmark_id": "bm_00001"},
    {"schedule_id": "", "place_id": "pc_00002", "bookmark_id": "bm_00002"},
    {"schedule_id": "", "place_id": "pc_00003", "bookmark_id": "bm_00003"},
    {"schedule_id": "", "place_id": "pc_00004", "bookmark_id": "bm_00004"},
    {"schedule_id": "", "place_id": "pc_00005", "bookmark_id": "bm_00005"},
    {"schedule_id": "", "place_id": "pc_00006", "bookmark_id": "bm_00005"},
    {"schedule_id": "", "place_id": "pc_00007", "bookmark_id": "bm_00005"},
    {"schedule_id": "", "place_id": "pc_00008", "bookmark_id": "bm_00005"},
    {"schedule_id": "", "place_id": "pc_00009", "bookmark_id": "bm_00005"},
    {"schedule_id": "sc_00001", "place_id": "", "bookmark_id": "bm_00006"},
    {"schedule_id": "sc_00002", "place_id": "", "bookmark_id": "bm_00007"},
    {"schedule_id": "sc_00003", "place_id": "", "bookmark_id": "bm_00008"},
    {"schedule_id": "sc_00004", "place_id": "", "bookmark_id": "bm_00009"},
    {"schedule_id": "sc_00005", "place_id": "", "bookmark_id": "bm_00010"},
    {"schedule_id": "sc_00006", "place_id": "", "bookmark_id": "bm_00011"},
]

    # 중복되지 않은 데이터만 삽입
new_bookmarklists = []
for data in bookmarklists:
    try:
        place = Place.objects.get(place_id=data["place_id"]) if data["place_id"] else None
        schedule = Schedule.objects.get(schedule_id=data["schedule_id"]) if data["schedule_id"] else None
        bookmark = Bookmark.objects.get(bookmark=data["bookmark_id"])
        
        # 중복 여부 확인
        if not BookmarkList.objects.filter(place=place, schedule=schedule, bookmark=bookmark).exists():
            new_bookmarklists.append(
                BookmarkList(
                    place=place,
                    schedule=schedule,
                    bookmark=bookmark,
                )
            )
    except Place.DoesNotExist:
        print(f"Place with ID '{data['place_id']}' does not exist.")
    except Schedule.DoesNotExist:
        print(f"Schedule with ID '{data['schedule_id']}' does not exist.")
    except Bookmark.DoesNotExist:
        print(f"Bookmark with ID '{data['bookmark_id']}' does not exist.")

# 새로운 데이터만 bulk_create
if new_bookmarklists:
    BookmarkList.objects.bulk_create(new_bookmarklists)
    print(f"{len(new_bookmarklists)}개의 BookmarkList 데이터가 추가되었습니다!")
else:
    print("중복 데이터가 존재하여 추가된 데이터가 없습니다.")
