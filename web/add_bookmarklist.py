import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import BookmarkList, Bookmark, BookmarkPlace, BookmarkSchedule

# BookmarkList 레코드 추가
bookmarklists = [
    {"bookmarkschedule_id": "", "bookmarkplace_id": "pc_00001", "bookmark_id": "bm_00001"},
    {"bookmarkschedule_id": "", "bookmarkplace_id": "pc_00002", "bookmark_id": "bm_00002"},
    {"bookmarkschedule_id": "", "bookmarkplace_id": "pc_00003", "bookmark_id": "bm_00003"},
    {"bookmarkschedule_id": "", "bookmarkplace_id": "pc_00004", "bookmark_id": "bm_00004"},
    {"bookmarkschedule_id": "", "bookmarkplace_id": "pc_00005", "bookmark_id": "bm_00005"},
    {"bookmarkschedule_id": "", "bookmarkplace_id": "pc_00006", "bookmark_id": "bm_00005"},
    {"bookmarkschedule_id": "", "bookmarkplace_id": "pc_00007", "bookmark_id": "bm_00005"},
    {"bookmarkschedule_id": "", "bookmarkplace_id": "pc_00008", "bookmark_id": "bm_00005"},
    {"bookmarkschedule_id": "", "bookmarkplace_id": "pc_00009", "bookmark_id": "bm_00005"},
    {"bookmarkschedule_id": "sc_00001", "bookmarkplace_id": "", "bookmark_id": "bm_00006"},
    {"bookmarkschedule_id": "sc_00002", "bookmarkplace_id": "", "bookmark_id": "bm_00007"},
    {"bookmarkschedule_id": "sc_00003", "bookmarkplace_id": "", "bookmark_id": "bm_00008"},
    {"bookmarkschedule_id": "sc_00004", "bookmarkplace_id": "", "bookmark_id": "bm_00009"},
    {"bookmarkschedule_id": "sc_00005", "bookmarkplace_id": "", "bookmark_id": "bm_00010"},
    {"bookmarkschedule_id": "sc_00006", "bookmarkplace_id": "", "bookmark_id": "bm_00011"},
]

    # 중복되지 않은 데이터만 삽입
new_bookmarklists = []
for data in bookmarklists:
    try:
        bookmarkplace = BookmarkPlace.objects.get(bookmarkplace_id=data["bookmarkplace_id"]) if data["bookmarkplace_id"] else None
        bookmarkschedule = BookmarkSchedule.objects.get(bookmarkschedule_id=data["bookmarkschedule_id"]) if data["bookmarkschedule_id"] else None
        bookmark = Bookmark.objects.get(bookmark=data["bookmark_id"])
        
        # 중복 여부 확인
        if not BookmarkList.objects.filter(bookmarkplace=bookmarkplace, bookmarkschedule=bookmarkschedule, bookmark=bookmark).exists():
            new_bookmarklists.append(
                BookmarkList(
                    bookmarkplace=bookmarkplace,
                    bookmarkschedule=bookmarkschedule,
                    bookmark=bookmark,
                )
            )
    except BookmarkPlace.DoesNotExist:
        print(f"Place with ID '{data['bookmarkplace_id']}' does not exist.")
        continue
    except BookmarkSchedule.DoesNotExist:
        print(f"Schedule with ID '{data['bookmarkschedule_id']}' does not exist.")
        continue
    except Bookmark.DoesNotExist:
        print(f"Bookmark with ID '{data['bookmarkbookmark_id']}' does not exist.")
        continue

# 새로운 데이터만 bulk_create
if new_bookmarklists:
    BookmarkList.objects.bulk_create(new_bookmarklists)
    print(f"{len(new_bookmarklists)}개의 BookmarkList 데이터가 추가되었습니다!")
else:
    print("중복 데이터가 존재하여 추가된 데이터가 없습니다.")
