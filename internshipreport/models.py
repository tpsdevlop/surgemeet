from djongo import models
from datetime import datetime


# Create your models here.
class StudentDetails(models.Model):
    StudentId       = models.CharField(max_length=15, primary_key=True)
    firstName       = models.CharField(max_length=20)
    lastName        = models.CharField(max_length=20)
    college_Id      = models.CharField(max_length=20)
    CollegeName     = models.CharField(max_length=20)
    Center          = models.CharField(max_length=20)
    email           = models.EmailField(unique=True)
    whatsApp_No     = models.IntegerField()
    mob_No          = models.IntegerField()
    sem             = models.CharField(max_length=3)
    branch          = models.CharField(max_length=10) 
    status          = models.CharField(max_length=3)
    user_category   = models.CharField(max_length=3)
    reg_date        = models.DateField()
    exp_date        = models.DateField()
    score           = models.FloatField()
    progress_Id     = models.JSONField(default=dict)
    Assignments_test= models.JSONField(default=dict)
    Courses         = models.JSONField(default=list)
    Course_Time     = models.JSONField(default=dict)
    CGPA            = models.FloatField(default=0.0)
    user_Type       = models.CharField(max_length=20,default='')
    class Meta:
        managed = False  
        db_table = 'Exskilence_studentdetails'


class StudentDetails_Days_Questions(models.Model):
    Student_id      = models.CharField(max_length=25,primary_key=True)
    Days_completed  = models.JSONField(default=dict)
    Qns_lists       = models.JSONField(default=dict)
    Qns_status      = models.JSONField(default=dict)
    Ans_lists       = models.JSONField(default=dict)
    Score_lists     = models.JSONField(default=dict)
    Start_Course    = models.JSONField(default=dict)
    End_Course      = models.JSONField(default=dict)
    class Meta:
        managed = False  
        db_table = 'Exskilence_studentdetails_days_questions'
    
     

class QuestionDetails_Days(models.Model):
    sl_no           = models.AutoField(primary_key=True)
    Student_id      = models.CharField(max_length=25)
    Subject         = models.CharField(max_length=25)
    Attempts        = models.IntegerField()
    DateAndTime     = models.DateTimeField()
    Score           = models.IntegerField()
    Qn              = models.TextField(max_length=25)
    Ans             = models.TextField()
    Result          = models.JSONField(default=dict)
    class Meta:
        managed = False  
        db_table = 'Exskilence_questiondetails_days'

class BugDetails(models.Model):
    sl_id = models.AutoField(primary_key=True)
    Student_id = models.CharField(max_length=25)
    Img_path = models.TextField()
    BugDescription = models.TextField()
    BugStatus = models.CharField(max_length=50, default='Pending')
    Issue_type = models.CharField(max_length=50)
    Reported = models.DateTimeField()
    Resolved = models.DateTimeField(null=True)
    Comments = models.JSONField(default=dict)
    class Meta:
        managed = False  
        db_table = 'Exskilence_bugdetails'

class Attendance (models.Model):
    Login_id        = models.AutoField(primary_key=True)
    SID             = models.CharField(max_length=15)
    Login_time      = models.DateTimeField()
    Last_update     = models.DateTimeField()
    Status          = models.TextField(default="in")
    Duration        = models.IntegerField(default=0)
    class Meta:
        managed = False  
        db_table = 'Exskilence_attendance'

class ErrorLogs(models.Model):
    Error_id        = models.AutoField(primary_key=True)
    StudentId       = models.CharField(max_length=15)
    Email           = models.EmailField()
    Name            = models.CharField(max_length=25)
    Occurred_time    = models.DateTimeField()
    Error_msg       = models.TextField()
    Stack_trace     = models.TextField()
    User_agent      = models.TextField()
    Operating_sys   = models.TextField()
    class Meta:
        managed = False  
        db_table = 'Exskilence_errorlogs'

class Rankings(models.Model):
    Rank_id      = models.AutoField(primary_key=True)
    StudentId   = models.CharField(max_length=15)
    Rank        = models.IntegerField()
    Course      = models.CharField(max_length=100)
    Score       = models.FloatField()
    DateTime    = models.DateTimeField()
    Delay       = models.FloatField()
    class Meta:
        managed = False  
        db_table = 'Exskilence_rankings'
class InternshipsDetails(models.Model):###
    ID             = models.AutoField( primary_key=True)
    StudentId      = models.CharField(max_length=25,unique=True)
    ProjectName    = models.JSONField(default=list)
    ProjectStatus  = models.JSONField(default=dict)
    SubmissionDates = models.JSONField(default=dict)
    ProjectDateAndTime = models.JSONField(default=dict)
   
    HTMLCode       = models.JSONField(default=dict)
    HTMLScore      = models.JSONField(default=dict)
 
    CSSCode        = models.JSONField(default=dict)
    CSSScore       = models.JSONField(default=dict)
 
    JSCode         = models.JSONField(default=dict)
    JSScore        = models.JSONField(default=dict)
 
    PythonCode     = models.JSONField(default=dict)
    PythonScore    = models.JSONField(default=dict)
 
    AppPyCode      = models.JSONField(default=dict)
    AppPyScore     = models.JSONField(default=dict)
 
    DatabaseCode   = models.JSONField(default=dict)
    DatabaseScore  = models.JSONField(default=dict)
 
    InternshipScores = models.JSONField(default=dict)
    class Meta:
        managed = False  
        db_table = 'Exskilence_internshipsdetails'
 