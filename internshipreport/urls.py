from django.urls import path
from .views import *
from .sqlpythonview import *
from .bugsview import *
from .adminflowview import *
from .adminsmyview import *
from .pythonrunningtest import *
urlpatterns = [
    path('student-details/', create_student_details, name='student-details-create'),
    path('student-details-days-questions/', create_student_details_days_questions, name='student-details-days-questions-create'),
    path('testest/',frontpagedeatialsmethod,name='testest'),
    # path('htmlcssview/',htmlcssview,name='htmlcssview'),
    path('per-student-data/',per_student_html_CSS_data,name='per-student-data'),
    path('per-student-JavaScript-data/',per_student_JS_data,name='per-student-JS-data'),
    path('per_ques_stu/',per_student_ques_detials,name='per_ques_stu'),    
    path('per_ques_JavaScript_stu/',per_student_JS_ques_detials,name='per_ques_stu'),    
    path('students/', student_list, name='student-list'),
    path('student-details-day/<str:student_id>/<str:course>/', student_details_day, name='student-details-day'),
    path('report/<str:student_id>/<str:course>/<str:day>/', getreport, name='getreport'),
    path('bugsoveriewpage/', get_students_with_bug_details, name='bugsoveriewpage'),
    path('bugs/', BugView.as_view(),name='bugs'),
    path('putStudentCommand/',add_student_comment, name='sendStudentCommand'),
    path('putTrainerCommand/',add_trainer_comment,name='putTrainerCommand'),
    path('reslovebug/',resolve_bug,name='reslovebug'),
    path ('getadminflow/', adminflow),
    path('bugs/reported/<str:period>/', get_bugs_reported_by_period, name='get_bugs_reported'),
    path('bugs/resolved/<str:period>/', get_bugs_resolved_by_period, name='get_bugs_resolved'),
    path('one_stu_data/', single_student_details, name='single_student_details'),
    path('bugscount/', get_bug_count, name='bugscount'),
    path('active-users/', get_active_users, name='active_users'),
    path('jjjjj/',getSTdDaysdetailes,name='jjjjj'),
    # path ('runpy/',run_python ),
]
