from django.contrib import admin
from .models import  Session, Participant, Log

# Register your models here.
admin.site.register(Session)
admin.site.register(Participant)
admin.site.register(Log)