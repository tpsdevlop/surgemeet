from django.db import models

class Session(models.Model):
    id = models.IntegerField(primary_key=True)
    Session_Topic = models.CharField(max_length=100)
    Date = models.DateField()
    Start_Time = models.CharField(max_length=20)
    conductedby = models.CharField(max_length=50)
    meetlink = models.URLField()
    Colleges = models.JSONField(default=list)  # Assuming it can have multiple colleges
    Branches = models.JSONField(default=list)  # Assuming it can have multiple branches

class Student(models.Model):
    session = models.ForeignKey(Session, related_name='students', on_delete=models.CASCADE)
    stuId = models.CharField(max_length=10)
    stuname = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    phonenumber = models.CharField(max_length=15,default="")
    branch = models.CharField(max_length=100)
    collegeName = models.CharField(max_length=100)
    email = models.EmailField()
