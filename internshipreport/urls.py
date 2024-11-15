from django.urls import path
from .views import *

urlpatterns = [
    path('testest/',frontpagedeatialsmethod,name='testest'),
]
