from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mainpage/', views.mainpage, name='mainpage'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('stdpage/', views.stdpage, name='stdpage'),
    path('parentpage/', views.parentpage, name='parentpage'),
    path('tchrpage/', views.tchrpage, name='tchrpage'),
]