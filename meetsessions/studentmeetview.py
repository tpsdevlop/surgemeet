from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Session
from googleMeet.models import Session as googleMeetSession, Participant
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse


@csrf_exempt
def fetch_student_attendance(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            student_id = body.get('student_id')
            if not student_id:
                return JsonResponse({"error": "student_id is required"}, status=400)
            sessions = Session.objects.all()
            session_data = []
            for session in sessions:
                studentsinvited_str = session.studentsinvited
                is_invited = check_student_invitation(studentsinvited_str, student_id)
                googleMeet_session = googleMeetSession.objects.filter(session_id=session.id).first()
                total_duration = googleMeet_session.session_duration if googleMeet_session else "0"
                attendance_info = {
                    'student_id': student_id,
                    'display_name': "Not Attended",
                    'attended_time': "Not Attended",
                    'attendance_percentage': 0
                }
                if is_invited:
                    try:
                        participant = Participant.objects.get(session_id=session.id, student_id=student_id)
                        attendance_info = {
                            'student_id': participant.student_id,
                            'display_name': participant.display_name,
                            'attended_time': participant.attended_time,
                            'attendance_percentage': calculate_attendance(participant.attended_time, total_duration)
                        }
                    except Participant.DoesNotExist:
                        pass  
                session_data.append({
                    'session_id': session.id,
                    'session_topic': session.Session_Topic,
                    'date': session.Date,
                    'start_time': session.Start_Time,
                    'conducted_by': session.conductedby,
                    'meet_link': session.meetlink,
                    'colleges': session.Colleges,
                    'branches': session.Branches,
                    'ended': session.ended,
                    'video_link': session.videoLink,
                    'attendance': attendance_info
                })

            if session_data:
                return JsonResponse(session_data, safe=False, status=200)
            else:
                return JsonResponse({"message": "No attendance data found for the given student."}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)

def calculate_attendance(attended_time, total_duration):
    try:
        attended_minutes = int(attended_time)
        total_minutes = int(total_duration)
        if total_minutes == 0:
            return 0.0
        attendance_percentage = (attended_minutes / total_minutes) * 100
        if attendance_percentage > 100:
            attendance_percentage = 100.0
            
        return round(attendance_percentage, 2)
    except ValueError:
        return 0.0 

def check_student_invitation(studentsinvited_str, student_id):
    try:
        return student_id in studentsinvited_str 
    except (json.JSONDecodeError, TypeError):
        return False  
