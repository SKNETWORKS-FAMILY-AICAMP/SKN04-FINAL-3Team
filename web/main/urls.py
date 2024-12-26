from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.main, name='main'),  # 독립적인 메인 페이지
    path('app/', views.spa, name='spa'),  # SPA 시작 페이지
    path('app/planner/', views.planner, name='planner'),
    path('app/profile/', views.profile, name='profile'),
    path('app/settings/', views.settings, name='settings'),
    path('app/myplace/', views.myplace, name='myplace'),
    path('app/chatting/', views.chatting, name='chatting'),
]