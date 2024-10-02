from django.urls import path
from . import views

urlpatterns = [
    path('create_session/', views.create_session, name='create_session'),
    path('sessions/all/', views.get_all_sessions, name='get_all_sessions'),
    path('sessions/<int:session_id>/', views.get_session_by_id, name='get_session_by_id'),
    path('create-sessionsep/', views.create_session2, name='sessionsep'),
    path('add-students/', views.add_students_to_session, name='add_students_to_session'),    
]
