from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(StudentDetails)
admin.site.register(StudentDetails_Days_Questions)
admin.site.register(QuestionDetails_Days)
admin.site.register(Attendance)