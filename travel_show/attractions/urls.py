from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),           # 首页
    path('search/', views.search, name='search'),
    path('province/<str:province_name>/', views.province_detail, name='province_detail'),
    path('city/<str:city_name>/', views.city_detail, name='city_detail'),
    path('ai/', views.ai_chat, name='ai_chat'),
]