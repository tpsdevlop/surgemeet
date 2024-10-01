# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('add_trainers/', views.add_user, name='add_user'),
    path('get_trainers/', views.get_all_users, name='admin_users'),
]
