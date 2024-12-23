from django.urls import path
from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    path('', views.map_view, name='map_view'),
    path('planner/', views.planner, name='planner'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('myplace/', views.myplace, name='myplace'),
]