from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('', views.index, name='index'),
    path('courses/', views.manage_courses, name='manage_courses'),
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/<int:pk>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('certificates/', views.manage_certificates, name='manage_certificates'),
    path('certificates/add/', views.add_certificate, name='add_certificate'),
    path('certificates/<int:pk>/edit/', views.edit_certificate, name='edit_certificate'),
    path('certificates/<int:pk>/revoke/', views.revoke_certificate, name='revoke_certificate'),
]
