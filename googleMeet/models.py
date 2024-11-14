from django.db import models

# Create your models here.
from djongo import models
from datetime import datetime, timedelta


class UserToken(models.Model):
    userEmail = models.EmailField(max_length=254,primary_key=True)
    token = models.JSONField()

    def __str__(self) -> str:
        return self.userEmail
    

class Session(models.Model):
    session_id = models.CharField(max_length=50, primary_key=True) 
    email = models.EmailField()  
    inst_name = models.CharField(max_length=100)  
    session_duration = models.CharField(max_length=20) 

    def __str__(self):
        return f"Session ID: {self.session_id}, Instructor: {self.inst_name},Duration:{self.session_duration}"
class Participant(models.Model):
    session = models.ForeignKey(Session, related_name='participants', on_delete=models.CASCADE)  
    student_id = models.CharField(max_length=50, null=True)  # Student ID
    display_name = models.CharField(max_length=100)  # Student's display name
    attended_time = models.CharField(max_length=20)  # Time attended by student

    def __str__(self):
        return f"Participant: {self.display_name} in Session: {self.session.session_id} {self.student_id} {self.attended_time}"
    
    participants_data = [
    {"student_id": "0001", "display_name": "Ranjitha A N", "attended_time": "5 minutes"},
    {"student_id": "0002", "display_name": "Sky is Blue", "attended_time": "8 minutes"},
]

class Log(models.Model):
    student_id = models.CharField(max_length=100,default="")
    session_id = models.CharField(max_length=100,default="")
    session_start_time = models.DateTimeField()  # Start time of the session
    session_end_time = models.DateTimeField()  # End time of the session

    def __str__(self):
        return f"Log for {self.participant.display_name} in Session: {self.participant.session.session_id}"

