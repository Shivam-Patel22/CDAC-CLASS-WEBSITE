from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('verify-certificate/', views.verify, name='verify'),
    path('verify/', views.verify, name='verify_alt'),
]
