from django.shortcuts import render
from django.conf import settings
from dotenv import load_dotenv
import os

load_dotenv()

def spa(request):
    return render(request, 'spa_base.html')  # Ajax로 로드될 템플릿

# 메인 페이지
def main(request):
    return render(request, 'main.html')  # 메인 화면 템플릿

def planner(request):
    ncp_client_id = os.getenv('NCP_CLIENT_ID')
    return render(request, 'partials/planner.html', {
        'ncp_client_id': ncp_client_id,
    })

def profile(request):
    return render(request, 'partials/profile.html')  # Ajax로 로드될 템플릿

def settings(request):
    return render(request, 'partials/settings.html')  # Ajax로 로드될 템플릿

def myplace(request):
    return render(request, 'partials/myplace.html')  # Ajax로 로드될 템플릿
