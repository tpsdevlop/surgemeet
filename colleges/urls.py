from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_college, name='create_college'),
    path('update/<int:college_id>/', views.update_college, name='update_college'),
    path('list/', views.list_colleges, name='list_colleges'),
]
