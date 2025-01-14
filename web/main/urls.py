from django.urls import path, re_path
from . import views

urlpatterns = [
    # 메인 페이지
    path('', views.main, name='main'),

    # 로그인
    path('login/', views.login_view, name='login'),
    path('login_process/', views.login_process, name='login_process'),
    path('logout/', views.logout_view, name='logout_view'),
    path('signup/', views.signup, name='signup'),
    path('signup_process/', views.signup_process, name='signup_process'),

    # Partial 전용 라우트
    path('app/partials/planner/', views.planner, name='planner'),
    path('app/partials/planner/run-gpt/', views.run_gpt_view, name='run_gpt'),
    path("app/partials/planner/get_or_create_chat_id/", views.get_or_create_chat_id, name="get_or_create_chat_id"),
    path('app/partials/planner/get_chat_content/', views.get_chat_content, name='get_chat_content'),
    path("app/partials/planner/get_title/", views.get_chat_title, name="get_chat_title"),
    path("app/partials/planner/update_title/", views.update_title, name="update_title"),
    path('app/partials/planner/check_duplicate_title/', views.check_duplicate_title, name='check_duplicate_title'),
    path("app/partials/planner/save_chat/", views.save_chat, name="save_chat"),
    path("app/partials/planner/init_chat/", views.init_chat, name="init_chat"),
    path('app/partials/chatting/', views.chatting, name='chatting'),
    path('app/partials/chatting/count/', views.get_chat_count, name='get_chat_count'),
    path('app/partials/chatting/delete/', views.delete_chat, name='delete_chat'),
    path('app/partials/favorites/', views.favorites_places, name='favorites_places'),
    path('app/partials/favorites/add/', views.add_folder, name='add_folder'),
    path('app/partials/favorites/delete/', views.delete_favorite, name='delete_favorite'),
    path('add_folder/', views.add_folder, name='add_folder'),  # 폴더 생성용 엔드포인트
    path('app/partials/settings/', views.settings, name='settings'),
    path('app/partials/settings/update_theme/', views.update_theme, name='update_theme'),
    path('app/partials/settings/update_language/', views.update_language, name='update_language'),
    path('app/partials/profile/', views.profile, name='profile'),
    path('app/partials/profile/update_thumbnail/', views.update_thumbnail, name='update_thumbnail'),
    path('app/partials/profile/update_nickname/', views.update_nickname, name='update_nickname'),

    # SPA Fallback
    re_path(r'^app(?:/.*)?$', views.spa, name='spa'),
    
]