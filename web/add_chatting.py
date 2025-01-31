import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from main.models import Chatting, CustomUser

# Chatting 레코드 추가
chattings = [
    {"chatting_id": "ch_00001", "profile": CustomUser.objects.get(username="user1"), "title": "chat1", "content": '''<나>반갑습니다!'''},
    {"chatting_id": "ch_00002", "profile": CustomUser.objects.get(username="user2"), "title": "chat1", "content": '''<나>안녕하세요?<봇>안녕하세요!'''},
    {"chatting_id": "ch_00003", "profile": CustomUser.objects.get(username="user3"), "title": "chat1", "content": '''<나>좋은 하루 되세요!'''},
    {"chatting_id": "ch_00004", "profile": CustomUser.objects.get(username="user1"), "title": "chat2", "content": '''<나>1<봇>2<나>3<봇>4<나>5<봇>6<나>7<봇>8<나>9<봇>10<나>11<봇>12<나>13<봇>14<나>15<봇>16<나>17<봇>18<나>19<봇>20<나>21<봇>22'''},
    {"chatting_id": "ch_00005", "profile": CustomUser.objects.get(username="user1"), "title": "chat3", "content": '''<나>감사합니다!<봇>감사합니다!<나>감사합니다?<봇>감사합니다?'''},
    {"chatting_id": "ch_00006", "profile": CustomUser.objects.get(username="user1"), "title": "chat4", "content": '''<나>장난하냐?<봇>죄송합니다...'''},
]

for chatting_data in chattings:
    if not Chatting.objects.filter(chatting_id=chatting_data["chatting_id"]).exists():
        Chatting.objects.create(**chatting_data)
    else:
        print(f"Chatting ID {chatting_data['chatting_id']} already exists. Skipping.")

print("Chatting 데이터 추가 완료!")
