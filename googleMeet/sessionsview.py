from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Log, Session, Participant
from datetime import datetime
import pytz
from student.models import Student
from meetsessions.models import Session as googlesesion

@csrf_exempt
def get_session_and_participant_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            
            if not session_id:
                return JsonResponse({'error': 'session_id is required.'}, status=400)
            
            # Retrieve the session
            try:
                session = Session.objects.get(session_id=session_id)
            except Session.DoesNotExist:
                return JsonResponse({'error': 'Session not found.'}, status=404)
            
            # Retrieve invited students list from googlesesion
            session_data = googlesesion.objects.filter(id=session_id).values().first()
            if not session_data:
                return JsonResponse({'error': 'Google session not found.'}, status=404)
            
            invited_students = session_data['studentsinvited']
            student_data = {student.stuId: student for student in Student.objects.all()}
            participants = Participant.objects.filter(session=session)
            
            # Session info dictionary
            session_info = {
                'sessionId': session.session_id,
                'email': session.email,
                'inst_name': session.inst_name,
                'session_duration': session.session_duration,
            }
            
            # Participant info list with additional student details
            participant_info = []
            participant_ids = set()  # Track participants' IDs to avoid duplicates later
            
            for participant in participants:
                student_id = participant.student_id
                participant_ids.add(student_id)
                
                # Get student details
                student = student_data.get(student_id)
                student_display_name = student.stuname if student else "Unknown"
                student_branch = student.branch if student else "Unknown"
                student_college_name = student.collegeName if student else "Unknown"
                student_email = student.email if student else "Unknown"
                student_phone_number = student.phonenumber if student else "Unknown"
                
                # Get attendance logs for the participant
                logs = Log.objects.filter(session_id=session.session_id, student_id=student_id)
                session_logs = [
                    {
                        'session_start_time': log.session_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'session_end_time': log.session_end_time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    for log in logs
                ]
                
                # Add participant details to the list
                participant_info.append({
                    'student_id': student_id,
                    'display_name': student_display_name,
                    'attendedTime': participant.attended_time,
                    'branch': student_branch,
                    'collegeName': student_college_name,
                    'email': student_email,
                    'phone_number': student_phone_number,
                    'log': session_logs,
                    'present': True  # Indicate the student attended
                })
            
            # Add invited students who didn't attend
            for invited_student_id in invited_students:
                if invited_student_id not in participant_ids:
                    invited_student = student_data.get(invited_student_id)
                    student_display_name = invited_student.stuname if invited_student else "Unknown"
                    student_branch = invited_student.branch if invited_student else "Unknown"
                    student_college_name = invited_student.collegeName if invited_student else "Unknown"
                    student_email = invited_student.email if invited_student else "Unknown"
                    student_phone_number = invited_student.phonenumber if invited_student else "Unknown"
                    
                    # Add non-attending invited student details with present=False
                    participant_info.append({
                        'student_id': invited_student_id,
                        'display_name': student_display_name,
                        'attendedTime': None,
                        'branch': student_branch,
                        'collegeName': student_college_name,
                        'email': student_email,
                        'phone_number': student_phone_number,
                        'log': [],
                        'present': False  # Indicate the student was invited but didn't attend
                    })
            
            # Response data with session and participant info
            response_data = {
                'sessionInfo': session_info,
                'participantInfo': participant_info
            }
            
            return JsonResponse(response_data, safe=False)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'POST method required.'}, status=405)