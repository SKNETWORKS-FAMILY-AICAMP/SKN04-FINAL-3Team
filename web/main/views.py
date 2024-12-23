from django.shortcuts import render
import os

def map_view(request):
    return render(request, 'index.html', {
        'ncp_client_id': os.getenv('NCP_CLIENT_ID'),  # 환경 변수에서 가져오기
    })

def home(request):
    return render(request, 'index.html')

def planner(request):
    return render(request, 'planner.html')

def profile(request):
    return render(request, 'profile.html')

def settings(request):
    return render(request, 'settings.html')

def myplace(request):
    return render(request, 'myplace.html')