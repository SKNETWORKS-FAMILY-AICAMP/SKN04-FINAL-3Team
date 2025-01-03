import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import Chatting, CustomUser

# Chatting 레코드 추가
chattings = [
    {"chatting_id": "ch_00001", "profile": CustomUser.objects.get(username="user1"), "content": "안녕하세요!"},
    {"chatting_id": "ch_00002", "profile": CustomUser.objects.get(username="user2"), "content": "반갑습니다!"},
    {"chatting_id": "ch_00003", "profile": CustomUser.objects.get(username="user3"), "content": "좋은 하루 되세요!"},
]

for chatting_data in chattings:
    if not Chatting.objects.filter(chatting_id=chatting_data["chatting_id"]).exists():
        Chatting.objects.create(**chatting_data)
    else:
        print(f"Chatting ID {chatting_data['chatting_id']} already exists. Skipping.")

print("Chatting 데이터 추가 완료!")
