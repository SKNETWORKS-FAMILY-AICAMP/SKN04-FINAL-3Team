from django.shortcuts import render
from dotenv import load_dotenv
import os

load_dotenv()

def spa(request):
    ncp_client_id = os.getenv('NCP_CLIENT_ID')  # 환경 변수에서 NCP_CLIENT_ID 가져오기
    print("DEBUG: NCP_CLIENT_ID =", ncp_client_id)  # 디버깅용 출력
    return render(request, 'spa_base.html', {
        'ncp_client_id': ncp_client_id,  # 템플릿에 전달
    })

# 메인 페이지
def main(request):
    return render(request, 'main.html')  # 메인 화면 템플릿

def planner(request):
    return render(request, 'partials/planner.html')  # 메인 화면 템플릿

def profile(request):
    return render(request, 'partials/profile.html')  # 메인 화면 템플릿

def settings(request):
    return render(request, 'partials/settings.html')  # 메인 화면 템플릿

def myplace(request):
    return render(request, 'partials/myplace.html')  # 메인 화면 템플릿

def chatting(request):
    return render(request, 'partials/chatting.html')  # 메인 화면 템플릿
