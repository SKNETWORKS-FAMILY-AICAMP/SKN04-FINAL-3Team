from django.shortcuts import render
from dotenv import load_dotenv
import os

load_dotenv()

def spa(request):
    ncp_client_id = os.getenv('NCP_CLIENT_ID')  # 환경 변수에서 NCP_CLIENT_ID 가져오기
    return render(request, 'spa_base.html', {
        'ncp_client_id': ncp_client_id,  # 템플릿에 전달
    })

# 메인 페이지
def main(request):
    return render(request, 'main.html')  

def planner(request):
    return render(request, 'partials/planner.html')  

def profile(request):
    return render(request, 'partials/profile.html')  

def settings(request):
    return render(request, 'partials/settings.html')  

def myplace(request):
    return render(request, 'partials/myplace.html')  

def chatting(request):
    return render(request, 'partials/chatting.html')  
