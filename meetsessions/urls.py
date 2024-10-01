from django.urls import path
from . import views

urlpatterns = [
    path('create_session/', views.create_session, name='create_session'),
    path('sessions/all/', views.get_all_sessions, name='get_all_sessions'),
    path('sessions/<int:session_id>/', views.get_session_by_id, name='get_session_by_id'),



    
]
