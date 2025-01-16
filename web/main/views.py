from langraph.langraph import run_gpt_api
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import models
from main.models import Chatting, Bookmark, Settings, Country, CustomUser
from dotenv import load_dotenv
import os
import json
import uuid


load_dotenv()

def spa(request):
    ncp_client_id = os.getenv('NCP_CLIENT_ID')  # 환경 변수에서 NCP_CLIENT_ID 가져오기
    context = {'ncp_client_id': ncp_client_id}  # 기본 컨텍스트
    context.update(get_theme_context(request.user))  # 테마 정보 추가
    return render(request, 'spa_base.html', context)


# 메인 페이지
def main(request):
    return render(request, 'main.html')  


def get_theme_context(user):
    if user and user.is_authenticated:
        try:
            settings = Settings.objects.get(profile=user)
            return {"settings": settings}
        except Settings.DoesNotExist:
            pass
    return {"settings": {"is_white_theme": True}}


# # (1) login_view: GET이면 login.html 렌더링
# def login_view(request):
#     countries = get_nationalities()
    
#     if request.method == 'GET':
#         return render(request, 'login.html', {
#             'countries': countries,  # 템플릿에 전달
#         })
#     else:
#         # 혹시 POST로 왔다면 login_process로 넘긴다
#         return redirect('login_process')
    
def login_view(request):
    if request.method == "GET":
        next_url = request.GET.get("next", "/")  # next 파라미터가 없으면 메인 페이지로 리다이렉트
        return render(request, "login.html", {"next": next_url})
    elif request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get("next", "/")  # POST로 넘어온 next 파라미터
            return redirect(next_url)
        else:
            return render(request, "login.html", {"error": "Invalid credentials", "next": request.POST.get("next", "/")})


def signup(request):
    countries = get_nationalities()
    return render(request, 'signup.html', {
        'countries': countries,  # 템플릿에 전달
    })


def get_nationalities():
    countries = Country.objects.filter().order_by(
        models.Case(
            models.When(country_id="US", then=0),
            models.When(country_id="KR", then=1),
            models.When(country_id="CN", then=2),
            models.When(country_id="JP", then=3),
            default=4,
        )
    )
    return countries


@csrf_exempt
def signup_process(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # 필수 입력값 검증
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()
            confirm_password = data.get("confirm_password", "").strip()
            nationality = data.get("nationality", "").strip()
            birthday = data.get("birthday", "").strip()
            gender = data.get("gender", None)  # 성별 추가

            # 필수 필드 확인
            if not username or not password or not confirm_password or not nationality or not birthday or gender is None:
                return JsonResponse({"success": False, "error": "모든 필드를 채워주세요."}, status=400)

            # 아이디 중복 체크
            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({"success": False, "error": "ID already exists"}, status=400)
            
            # 비밀번호와 비밀번호 확인 일치 여부 확인
            if password != confirm_password:
                return JsonResponse({"success": False, "error": "Passwords do not match"}, status=400)

            # 성별 유효성 검사
            if gender not in [0, 1, 2]:  # 0: Not Specified, 1: Male, 2: Female
                return JsonResponse({"success": False, "error": "Invalid gender value"}, status=400)

            # 사용자 생성
            new_user = CustomUser.objects.create(
                username=username,
                password=make_password(password),  # 비밀번호 해시 처리
                country_id=nationality,
                birthday=birthday,
                gender=gender,  # 성별 저장
            )

            # Settings 테이블에 기본 설정 생성
            default_country = Country.objects.get(country_id=nationality)  # 가입한 국가와 연결
            Settings.objects.create(
                profile=new_user,
                country=default_country,  # 사용자의 국가 정보
                is_white_theme=True  # 기본값으로 White Theme 설정
            )

            return JsonResponse({"success": True})
        except Country.DoesNotExist:
            return JsonResponse({"success": False, "error": "Invalid nationality"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    else:
        return JsonResponse({"success": False, "error": "POST 요청만 허용됩니다."}, status=405)


# (2) login_process: 아이디/비번 둘 다 있으면 메인화면으로 이동
def login_process(request):
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        password = request.POST.get('password','').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # 세션에 로그인 상태 기록
            return redirect('/..')
        else:
            # 로그인 실패 -> 다시 login.html
            return render(request, 'login.html', {
                'error': '아이디나 비밀번호가 올바르지 않습니다.'
            })
    else:
        return redirect('login')


def logout_view(request):
    logout(request)  # 세션에서 사용자 정보 삭제
    return redirect('main')  # 로그아웃 후 로그인 페이지로 리다이렉트


@csrf_exempt
def planner(request):
    context = {}

    # 비로그인 사용자는 기본값으로 None 대신 AnonymousUser를 사용
    user = request.user if request.user.is_authenticated else None
    
    # get_theme_context 호출 시, user가 None이어도 안전하게 처리
    context.update(get_theme_context(user))

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chat_id = data.get("chat_id")
            new_message = data.get("content", "")  # 새로 입력된 메시지
            title = data.get("title", "Untitled")  # 기본 제목

            if not chat_id:
                # 로그인하지 않은 사용자에게 임의 chat_id 생성
                chat_id = f"guest_{uuid.uuid4().hex[:8]}"  # 비로그인 사용자용 chat_id

            if not user:  # 비로그인 사용자는 데이터베이스에 저장하지 않음
                return JsonResponse({"success": True, "chat_id": chat_id, "content": new_message})

            # 로그인된 사용자만 데이터 저장
            chat, created = Chatting.objects.get_or_create(
                chatting_id=chat_id,
                profile=request.user,
                defaults={"content": "", "title": title}
            )
            chat.content += f"\n{new_message}"
            chat.save()

            return JsonResponse({"success": True, "chat_id": chat_id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    elif request.method == "GET":
        chat_id = request.GET.get("chat_id", None)
        chat_content = ""
        if chat_id and user:
            try:
                chat = Chatting.objects.get(chatting_id=chat_id, profile=user)
                chat_content = chat.content
            except Chatting.DoesNotExist:
                pass

        # 비로그인 사용자도 기본 데이터를 제공
        context.update({"chat_content": chat_content})
        return render(request, "partials/planner.html", context)


def check_duplicate_title(request):
    """
    채팅 제목 중복 확인 API
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title", "").strip()

            if Chatting.objects.filter(title=title, profile=request.user).exists():
                return JsonResponse({"is_duplicate": True})
            return JsonResponse({"is_duplicate": False})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
@login_required
def update_title(request):
    """DB에 채팅 제목 업데이트"""
    if request.method == "POST":
        data = json.loads(request.body)
        chat_id = data.get("chat_id")
        title = data.get("title")

        if not chat_id or not title:
            return JsonResponse({"success": False, "error": "Invalid data"})

        try:
            chat = Chatting.objects.get(chatting_id=chat_id, profile=request.user)
            chat.title = title
            chat.save()
            return JsonResponse({"success": True})
        except Chatting.DoesNotExist:
            return JsonResponse({"success": False, "error": "Chat not found"})

    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def get_chat_content(request):
    """
    특정 chat_id에 해당하는 채팅 내용을 반환합니다.
    """
    chat_id = request.GET.get('chat_id', None)
    if not chat_id:
        return JsonResponse({"success": False, "error": "chat_id가 제공되지 않았습니다."}, status=400)

    try:
        chat = Chatting.objects.get(chatting_id=chat_id, profile=request.user)
        print("chatcontent:", chat.content)
        return JsonResponse({"success": True, "content": chat.content})
    except Chatting.DoesNotExist:
        return JsonResponse({"success": False, "error": "해당 chat_id에 대한 채팅이 존재하지 않습니다."}, status=404)


def get_chat_title(request):
    chat_id = request.GET.get("chat_id")
    if not chat_id:
        return JsonResponse({"success": False, "error": "Missing chat_id"})

    try:
        if request.user.is_authenticated:
            chat = Chatting.objects.get(chatting_id=chat_id, profile=request.user)
        else:
            # 비로그인 사용자는 기본 제목 반환
            return JsonResponse({"success": True, "title": "Default Title"})
        return JsonResponse({"success": True, "title": chat.title})
    except Chatting.DoesNotExist:
        return JsonResponse({"success": False, "error": "Chat not found"})
    

@login_required
def get_chat_count(request):
    """
    현재 사용자의 채팅 개수를 반환합니다.
    """
    try:
        user_chat_count = Chatting.objects.filter(profile=request.user).count()
        return JsonResponse({"success": True, "chat_count": user_chat_count})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def profile(request):
    context = get_theme_context(request.user)  # 테마 정보 추가
    profile_user = request.user
    image_range = range(1, 11)  # 1부터 10까지의 숫자
    context.update({
        'profile_user': profile_user,
        'image_range': image_range,
    })  # 추가 정보 업데이트
    return render(request, 'partials/profile.html', context)


@csrf_exempt
@login_required
def update_thumbnail(request):
    """
    POST 요청으로 thumbnail_id 업데이트
    {
        "thumbnail_id": 1
    }
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            thumbnail_id = int(data.get("thumbnail_id", 0))

            if thumbnail_id < 1 or thumbnail_id > 10:
                return JsonResponse({"success": False, "error": "Invalid thumbnail ID."}, status=400)

            # 현재 로그인 사용자의 thumbnail_id 업데이트
            user = request.user
            user.thumbnail_id = thumbnail_id
            user.save()

            return JsonResponse({"success": True, "message": "Thumbnail updated successfully."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    else:
        return JsonResponse({"success": False, "error": "POST method required."}, status=405)


@csrf_exempt
@login_required
def update_nickname(request):
    """
    닉네임 업데이트 엔드포인트
    POST 요청:
    {
        "nickname": "새 닉네임"
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # JSON 형식 요청 파싱
            new_nickname = data.get('nickname', '').strip()

            if not new_nickname:
                return JsonResponse({"success": False, "error": "닉네임이 비어있습니다."}, status=400)

            # 로그인한 사용자의 닉네임 업데이트
            user = request.user
            user.nickname = new_nickname
            user.save()

            return JsonResponse({"success": True, "message": "닉네임이 성공적으로 업데이트되었습니다."})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "잘못된 JSON 요청입니다."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    else:
        return JsonResponse({"success": False, "error": "POST 요청만 허용됩니다."}, status=405)


@login_required
def settings(request):
    """
    Settings 페이지 렌더링. 현재 사용자와 연결된 Settings 데이터를 가져와서
    라디오 버튼 및 드롭다운 초기값 설정.
    """
    user = request.user

    try:
        # 현재 사용자와 연결된 Settings 객체 가져오기
        settings = Settings.objects.select_related('country').get(profile=user)

        return render(request, 'partials/settings.html', {
            'settings': settings,
            'language': settings.country.language,  # Settings에서 연결된 Country의 언어
            'country_id': settings.country.country_id,  # Settings에서 연결된 Country의 ID
        })
    except Settings.DoesNotExist:
        # Settings가 없는 경우 기본값 전달
        return render(request, 'partials/settings.html', {
            'settings': None,
            'language': None,
            'country_id': None,
        })
 

@csrf_exempt
@login_required
def update_theme(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            is_white_theme = data.get("is_white_theme", True)

            settings = Settings.objects.filter(profile=request.user).first()
            if not settings:
                settings = Settings.objects.create(profile=request.user, is_white_theme=is_white_theme)
            else:
                settings.is_white_theme = is_white_theme
                settings.save()

            return JsonResponse({"success": True, "message": "Theme updated successfully."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
        

@login_required
@csrf_exempt
def update_language(request):
    """
    POST 요청을 받아 settings 테이블의 country_id 값을 업데이트합니다.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_language = data.get("language")

            if not new_language:
                return JsonResponse({"success": False, "message": "Language not provided"}, status=400)

            # 현재 사용자의 Settings 가져오기
            settings = Settings.objects.filter(profile=request.user).first()
            if not settings:
                return JsonResponse({"success": False, "message": "Settings not found"}, status=404)

            # Country 검증
            valid_countries = ["US", "KR", "JP", "CN"]
            if new_language not in valid_countries:
                return JsonResponse({"success": False, "message": "Invalid language"}, status=400)

            # country_id 업데이트
            settings.country_id = new_language
            settings.save()

            return JsonResponse({"success": True, "message": "Language updated successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)
    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        

@login_required
def favorites_places(request):
    context = get_theme_context(request.user)  # 테마 정보 추가
    user = request.user
    places = Bookmark.objects.filter(profile=user, is_place=True)
    schedules = Bookmark.objects.filter(profile=user, is_place=False)
    context.update({
        "places": places,
        "schedules": schedules,
    })  # 추가 정보 업데이트
    return render(request, "partials/favorites_places.html", context)


@csrf_exempt
@login_required
def add_folder(request):
    """
    POST 예: {
      "title": "...",
      "is_place": true/false
    }
    bookmark_id는 "bm_00001" 등으로 자동 생성.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title", "").strip()
            if not title:
                return JsonResponse({"success": False, "error": "No folder name provided."}, status=400)

            is_place_value = data.get("is_place", True)

            # 1) Bookmark 중 "bm_xxxxx" 형태인 것들 중, 가장 큰 번호를 찾기
            last_bm = Bookmark.objects.filter(bookmark__startswith="bm_").order_by('-bookmark').first()
            if last_bm:
                # "bm_00009" -> split("_")[1] => "00009"
                numeric_str = last_bm.bookmark.split("_")[1]  
                last_num = int(numeric_str)  # 9
                new_num = last_num + 1       # 10
            else:
                # 아직 하나도 "bm_..." 형식이 없다면 1부터 시작
                new_num = 1

            # 2) zero-padding: 5자리를 맞춤 ("00001", "00010", ...)
            new_num_str = str(new_num).zfill(5)  
            # 3) 최종 bookmark_id
            new_id = f"bm_{new_num_str}"

            # 4) DB에 생성
            new_bookmark = Bookmark.objects.create(
                bookmark=new_id,
                profile=request.user,
                title=title,
                is_place=is_place_value
            )

            return JsonResponse({
                "success": True,
                "folderId": new_bookmark.bookmark,
                "message": f"Folder '{title}' created successfully."
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    else:
        return JsonResponse({"success": False, "error": "POST method required."}, status=405)
    

@csrf_exempt
@login_required
def delete_favorite(request):
    """
    즐겨찾기(폴더) 삭제용 예시. 
    POST 바디: {"bookmark_id": ...}
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            bookmark_id = data.get("bookmark_id")
            bookmark = Bookmark.objects.get(bookmark=bookmark_id, profile=request.user)
            bookmark.delete()
            return JsonResponse({"success": True})
        except Bookmark.DoesNotExist:
            return JsonResponse({"success": False, "error": "Bookmark not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required
def chatting(request):
    context = get_theme_context(request.user)  # 테마 정보 추가
    user = request.user
    chattings = Chatting.objects.filter(profile=user).order_by('created_at')
    context.update({
        'chattings': chattings,  
    })
    return render(request, 'partials/chatting.html', context)


@csrf_exempt
@login_required
def delete_chat(request):
    """
    채팅 삭제 API
    POST 요청:
    {
        "chatting_id": "chat_12345"
    }
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chatting_id = data.get("chatting_id")

            if not chatting_id:
                return JsonResponse({"success": False, "error": "Chat ID not provided."}, status=400)

            # 현재 사용자의 채팅 확인 및 삭제
            chat = Chatting.objects.filter(chatting_id=chatting_id, profile=request.user).first()
            if not chat:
                return JsonResponse({"success": False, "error": "Chat not found or unauthorized."}, status=404)

            chat.delete()
            return JsonResponse({"success": True, "message": "Chat deleted successfully."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)


def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return HttpResponseForbidden("You do not have admin access.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def run_gpt_view(request):
    if request.method == "POST":
        try:
            # JSON 데이터 파싱
            data = json.loads(request.body)
            user_input = data.get("question")

            if not user_input:
                return JsonResponse({"error": "Invalid input"}, status=400)
            print("q:", user_input)
            # run_gpt_api 호출
            answer = run_gpt_api(user_input)
            print("a:", answer)

            return JsonResponse({"answer": answer}, status=200)

        except Exception as e:
            # 에러 로그 출력
            print("Error in run_gpt_view:", e)
            return JsonResponse({"error": "Internal server error"}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)