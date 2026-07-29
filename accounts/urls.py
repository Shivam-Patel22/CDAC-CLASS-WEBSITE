from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.login, name='root_login'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('guest-login/', views.guest_login, name='guest_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
