import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import Country

# 기존 데이터를 삭제
Country.objects.all().delete()

# 새로운 데이터 삽입
countries = [
    Country(country_id="US", country_name="USA", language="English"),
    Country(country_id="KR", country_name="대한민국", language="한국어"),
    Country(country_id="CN", country_name="中国", language="汉文"),
    Country(country_id="JP", country_name="日本", language="日本語"),
]

Country.objects.bulk_create(countries)
print("Country 데이터 추가 완료!")
