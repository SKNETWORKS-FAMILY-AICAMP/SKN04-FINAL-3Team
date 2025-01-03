import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

# Django ORM 코드 실행
from main.models import Place

# 새로운 Place 레코드 추가
places = [
    Place(place_id="PLACE001", longitude=126.978, latitude=37.566, overview="서울시청"),
    Place(place_id="PLACE002", longitude=127.027, latitude=37.497, overview="강남역"),
    Place(place_id="PLACE003", longitude=126.952, latitude=37.579, overview="경복궁"),
    Place(place_id="PLACE004", longitude=129.075, latitude=35.179, overview="부산 광안대교"),
    Place(place_id="PLACE005", longitude=128.614, latitude=35.871, overview="대구 동성로"),
    Place(place_id="PLACE006", longitude=126.705, latitude=37.456, overview="인천 차이나타운"),
    Place(place_id="PLACE007", longitude=127.491, latitude=36.642, overview="대전 유성온천"),
    Place(place_id="PLACE008", longitude=127.254, latitude=37.001, overview="춘천 남이섬"),
    Place(place_id="PLACE009", longitude=127.531, latitude=37.886, overview="남양주 다산유적지"),
    Place(place_id="PLACE010", longitude=129.311, latitude=35.538, overview="울산 태화강 국가정원"),
]

# bulk_create를 사용하여 한 번에 삽입
Place.objects.bulk_create(places)

print("여러 Place 추가 완료!")
