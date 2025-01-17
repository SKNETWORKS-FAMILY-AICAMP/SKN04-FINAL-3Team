import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

# Django ORM 코드 실행
from main.models import BookmarkPlace

# 새로운 Place 레코드 추가
places = [
    # 용산구 명소
    {"bookmarkplace_id": "pc_00001", "address": "서울특별시 용산구 서빙고로 137", "name": "국립중앙박물관", "longitude": 126.980, "latitude": 37.523, "overview": "한국의 대표적인 박물관"},
    {"bookmarkplace_id": "pc_00002", "address": "서울특별시 용산구 이태원로", "name": "이태원", "longitude": 126.994, "latitude": 37.534, "overview": "다양한 외국 문화를 체험할 수 있는 거리"},
    {"bookmarkplace_id": "pc_00003", "address": "서울특별시 용산구 남산공원길 105", "name": "남산공원", "longitude": 126.980, "latitude": 37.550, "overview": "서울의 대표적인 공원"},
    {"bookmarkplace_id": "pc_00004", "address": "서울특별시 용산구 청파로 74", "name": "용산전자상가", "longitude": 126.964, "latitude": 37.529, "overview": "전자제품과 부품을 구매할 수 있는 상가"},
    {"bookmarkplace_id": "pc_00005", "address": "서울특별시 용산구 한남대로", "name": "한강진 카페거리", "longitude": 126.987, "latitude": 37.541, "overview": "개성 넘치는 카페가 모여 있는 거리"},
    {"bookmarkplace_id": "pc_00006", "address": "서울특별시 용산구 한강대로21길 40", "name": "드래곤힐 스파", "longitude": 126.970, "latitude": 37.537, "overview": "서울의 대표적인 찜질방"},
    {"bookmarkplace_id": "pc_00007", "address": "서울특별시 용산구 효창원로 177", "name": "효창공원", "longitude": 126.961, "latitude": 37.540, "overview": "서울의 독립운동 기념공원"},
    {"bookmarkplace_id": "pc_00008", "address": "서울특별시 용산구 서빙고로 77", "name": "용산가족공원", "longitude": 126.963, "latitude": 37.523, "overview": "가족 단위로 즐길 수 있는 공원"},

    # 중구 명소
    {"bookmarkplace_id": "pc_00009", "address": "서울특별시 중구 남대문시장4길 21", "name": "남대문시장", "longitude": 126.977, "latitude": 37.560, "overview": "한국 최대의 재래시장"},
    {"bookmarkplace_id": "pc_00010", "address": "서울특별시 중구 명동길 74", "name": "명동성당", "longitude": 126.986, "latitude": 37.563, "overview": "서울에서 가장 오래된 성당"},
    {"bookmarkplace_id": "pc_00011", "address": "서울특별시 중구 세종대로 99", "name": "덕수궁", "longitude": 126.975, "latitude": 37.566, "overview": "조선 시대의 궁궐 중 하나"},
    {"bookmarkplace_id": "pc_00012", "address": "서울특별시 중구 청파로 432", "name": "서울로 7017", "longitude": 126.971, "latitude": 37.554, "overview": "도심 속 공중보행로"},
    {"bookmarkplace_id": "pc_00013", "address": "서울특별시 용산구 남산공원길 105", "name": "남산타워", "longitude": 126.989, "latitude": 37.551, "overview": "서울의 상징적인 타워"},
    {"bookmarkplace_id": "pc_00014", "address": "서울특별시 중구 정동길", "name": "정동길", "longitude": 126.969, "latitude": 37.566, "overview": "역사와 현대가 공존하는 거리"},
    {"bookmarkplace_id": "pc_00015", "address": "서울특별시 종로구 새문안로 55", "name": "서울역사박물관", "longitude": 126.969, "latitude": 37.571, "overview": "서울의 역사를 볼 수 있는 박물관"},
    {"bookmarkplace_id": "pc_00016", "address": "서울특별시 중구 을지로 13길", "name": "을지로 노가리 골목", "longitude": 126.991, "latitude": 37.566, "overview": "소소한 골목 분위기를 즐길 수 있는 곳"},
    
    # 종로구 명소
    {"bookmarkplace_id": "pc_00017", "address": "서울특별시 종로구 사직로 161", "name": "경복궁", "longitude": 126.977, "latitude": 37.578, "overview": "조선 왕조의 궁궐"},
    {"bookmarkplace_id": "pc_00018", "address": "서울특별시 종로구 인사동길", "name": "인사동", "longitude": 126.985, "latitude": 37.571, "overview": "전통과 현대가 어우러진 거리"},
    {"bookmarkplace_id": "pc_00019", "address": "서울특별시 종로구 북촌로 10길", "name": "북촌 한옥마을", "longitude": 126.984, "latitude": 37.582, "overview": "전통 한옥의 멋을 느낄 수 있는 마을"},
    {"bookmarkplace_id": "pc_00020", "address": "서울특별시 종로구 율곡로 99", "name": "창덕궁", "longitude": 126.991, "latitude": 37.578, "overview": "조선 시대의 별궁"},
    {"bookmarkplace_id": "pc_00021", "address": "서울특별시 종로구 종로 157", "name": "종묘", "longitude": 126.994, "latitude": 37.572, "overview": "조선 왕실의 사당"},
    {"bookmarkplace_id": "pc_00022", "address": "서울특별시 종로구 세종대로 175", "name": "광화문광장", "longitude": 126.976, "latitude": 37.570, "overview": "서울의 중심 광장"},
    {"bookmarkplace_id": "pc_00023", "address": "서울특별시 종로구 청계천로", "name": "청계천", "longitude": 126.977, "latitude": 37.568, "overview": "서울 도심 속의 산책로"},
    {"bookmarkplace_id": "pc_00024", "address": "서울특별시 종로구 대학로", "name": "대학로", "longitude": 126.998, "latitude": 37.581, "overview": "연극과 문화가 어우러진 거리"},
    
    # 강남구 명소
    {"bookmarkplace_id": "pc_00025", "address": "서울특별시 강남구 영동대로 513", "name": "코엑스", "longitude": 127.060, "latitude": 37.512, "overview": "대형 전시 및 쇼핑몰"},
    {"bookmarkplace_id": "pc_00026", "address": "서울특별시 강남구 신사동 도산대로", "name": "가로수길", "longitude": 127.023, "latitude": 37.518, "overview": "트렌디한 맛집과 카페가 모여 있는 거리"},
    {"bookmarkplace_id": "pc_00027", "address": "서울특별시 강남구 봉은사로 531", "name": "삼성동 봉은사", "longitude": 127.057, "latitude": 37.514, "overview": "서울의 대표적인 사찰"},
    {"bookmarkplace_id": "pc_00028", "address": "서울특별시 강남구 강남대로", "name": "강남역", "longitude": 127.027, "latitude": 37.497, "overview": "서울의 대표 번화가"},
    {"bookmarkplace_id": "pc_00029", "address": "서울특별시 서초구 올림픽대로 683", "name": "세빛섬", "longitude": 127.101, "latitude": 37.516, "overview": "한강 위의 인공섬"},
    {"bookmarkplace_id": "pc_00030", "address": "서울특별시 강남구 압구정로", "name": "압구정 로데오거리", "longitude": 127.035, "latitude": 37.527, "overview": "고급 브랜드가 모여 있는 거리"},
    {"bookmarkplace_id": "pc_00031", "address": "서울특별시 강남구 남부순환로 2947", "name": "대치동 학원가", "longitude": 127.063, "latitude": 37.499, "overview": "대한민국 교육의 중심지"},
    {"bookmarkplace_id": "pc_00032", "address": "서울특별시 강남구 청담동 청담로", "name": "청담동 명품거리", "longitude": 127.050, "latitude": 37.524, "overview": "명품 브랜드와 고급 레스토랑이 모여 있는 거리"},
]

# 중복 방지 로직
new_places = []
for data in places:
    if not BookmarkPlace.objects.filter(place_id=data["place_id"]).exists():
        new_places.append(BookmarkPlace(**data))

# 새로운 데이터만 bulk_create
if new_places:
    BookmarkPlace.objects.bulk_create(new_places)
    print(f"{len(new_places)}개의 Place 데이터가 추가되었습니다!")
else:
    print("중복 데이터가 존재하여 추가된 데이터가 없습니다.")