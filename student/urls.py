from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_student, name='create_student'),
    path('getStudents/', views.get_all_students, name='get_all_students'),
    path('get_student_by_id/<str:stuId>/', views.get_student_by_id, name='get_student_by_id'),
    path('create_multiple/', views.create_multiple_students, name='create_multiple_students'),
]
