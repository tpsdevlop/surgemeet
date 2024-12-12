from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime, timedelta
ONTIME = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
# Create your views here.
def home (request):
    return HttpResponse('Welcome to the good home page push :'+str(ONTIME))