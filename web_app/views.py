from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def home (request):
    return HttpResponse('Welcome to the good home page push push 071024v1')