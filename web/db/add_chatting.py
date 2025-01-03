import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import Chatting, CustomUser

# Chatting 레코드 추가
chattings = [
    Chatting(chatting_id="ch_00001", profile=CustomUser.objects.get(username="user1"), content="안녕하세요, 서울에서 가입했습니다."),
    Chatting(chatting_id="ch_00002", profile=CustomUser.objects.get(username="user2"), content="Hello from New York!"),
    Chatting(chatting_id="ch_00003", profile=CustomUser.objects.get(username="user3"), content="こんにちは、東京から参加しました。"),
]

Chatting.objects.bulk_create(chattings)

print("Chatting 데이터 추가 완료!")
