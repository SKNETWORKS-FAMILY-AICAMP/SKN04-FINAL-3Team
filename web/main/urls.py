from django.urls import path, re_path
from . import views

urlpatterns = [
    # 메인 페이지(독립적인 화면)
    path('', views.main, name='main'),

    # 로그인
    path('login/', views.login_view, name='login'),
    path('login_process/', views.login_process, name='login_process'),
    path('signup/', views.signup, name='signup'),

    # (2) Partial 전용 라우트: SPA에서 Ajax로 불러오는 템플릿들
    path('app/partials/planner/', views.planner, name='planner'),
    path('app/partials/profile/', views.profile, name='profile'),
    path('app/partials/settings/', views.settings, name='settings'),
    path('app/partials/favorites/', views.favorites_places, name='favorites_places'),
    path('app/partials/chatting/', views.chatting, name='chatting'),

    # (1) SPA Fallback: /app/ 이하 모든 경로 -> spa_base.html 리턴
    re_path(r'^app(?:/.*)?$', views.spa, name='spa'),
]