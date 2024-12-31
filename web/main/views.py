from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
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

# (1) login_view: GET이면 login.html 렌더링
def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        # 혹시 POST로 왔다면 login_process로 넘긴다
        return redirect('login_process')

# (2) login_process: 아이디/비번 둘 다 있으면 /app/profile/로 리다이렉트
@csrf_protect
def login_process(request):
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        password = request.POST.get('password','').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # 세션에 로그인 상태 기록
            return redirect('/app/profile/')
        else:
            # 로그인 실패 -> 다시 login.html
            return render(request, 'login.html', {
                'error': '아이디나 비밀번호가 올바르지 않습니다.'
            })
    else:
        return redirect('login')

def logout_view(request):
    logout(request)  # 세션에서 사용자 정보 삭제
    return redirect('login')  # 로그아웃 후 로그인 페이지로 리다이렉트

def planner(request):
    return render(request, 'partials/planner.html')  
    
def profile(request):
    if not request.user.is_authenticated:
        return render(request, 'login.html') 
    return render(request, 'partials/profile.html')

def settings(request):
    return render(request, 'partials/settings.html')  

def favorites_places(request):
    return render(request, 'partials/favorites_places.html')

def favorites_schedules(request):
    return render(request, 'partials/favorites_schedules.html') 

def chatting(request):
    return render(request, 'partials/chatting.html')  
