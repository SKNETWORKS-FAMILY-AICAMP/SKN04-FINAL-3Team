from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', views.main, name='main'),  # 독립적인 메인 페이지
    path('app/', views.spa, name='spa'),  # SPA 시작 페이지
    # path('app/', RedirectView.as_view(url='/app/planner/', permanent=False)),
    path('app/planner/', views.planner, name='planner'),
    path('app/profile/', views.profile, name='profile'),
    path('app/settings/', views.settings, name='settings'),
    path('app/myplace/', views.myplace, name='myplace'),
    path('app/chatting/', views.chatting, name='chatting'),
]