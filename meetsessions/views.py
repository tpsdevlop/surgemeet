from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Max
import json
import smtplib
import ssl
import certifi
from .models import Session, Student  # Adjust the import path according to your project structure

@csrf_exempt
@require_http_methods(["POST"])
def create_session2(request):
    data = json.loads(request.body)
    try:
        # Get the current maximum id and calculate the new id
        max_id = Session.objects.aggregate(Max('id'))['id__max']
        new_id = (max_id or 0) + 1
        
        # Create a new session object with all fields explicitly included
        session = Session.objects.create(
            id=new_id,
            Session_Topic=data['Session_Topic'],
            Date=data['Date'],
            Start_Time=data['Start_Time'],
            conductedby=data['conductedby'],
            meetlink=data['meetlink'],
            Colleges=data['Colleges'],
            Branches=data['Branches'],
            ended=False, 
            videoLink="",  
            studentsinvited = []
        )
        return JsonResponse({'message': 'Session created successfully', 'session_id': session.id}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
# @csrf_exempt
# @require_http_methods(["POST"])
# def add_students_to_session(request):
#     data = json.loads(request.body)
#     try:
#         session_id = data['session_id']
#         session = Session.objects.get(id=session_id)
#         recipient_emails = []
#         for student_data in data['Students']:
#             try:
#                 Student.objects.create(
#                     session=session,
#                     stuId=student_data['stuId'],
#                     stuname=student_data['stuname'],
#                     gender=student_data['gender'],
#                     phonenumber=student_data['phonenumber'],
#                     branch=student_data['branch'],
#                     collegeName=student_data['collegeName'],
#                     email=student_data['email']
#                 )
#                 recipient_emails.append(student_data['email'])
#             except Exception as e:
#                 print(f"Error creating student: {e}")
        
#         # Prepare email details
#         subject = f"Details for the {session.Session_Topic} session"
#         message = f"""
#         Hello,

#         You have been registered for the session: {session.Session_Topic}.
#         Details are as follows:
#         Date: {session.Date}
#         Time: {session.Start_Time}
#         Conducted by: {session.conductedby}
#         Meet Link: {session.meetlink}

#         Regards,
#         Your Team
#         """
#         from_email = settings.EMAIL_HOST_USER

#         send_session_email(subject, message, from_email, recipient_emails)
        
#         return JsonResponse({'message': 'Students added and emails sent successfully'}, status=201)
#     except Session.DoesNotExist:
#         return JsonResponse({'error': 'Session not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def add_students_to_session(request):
    data = json.loads(request.body)
    try:
        session_id = data['session_id']
        session = Session.objects.get(id=session_id)
        sessiontopic = session.Session_Topic
        
        recipient_emails = []
        new_students = []
        
        for student_data in data['Students']:
            try:
                # Only collect the student ID and email, without creating new Student objects
                new_students.append(student_data['stuId'])  # Collect student IDs to update `studentsinvited`
                recipient_emails.append(student_data['email'])
            except Exception as e:
                print(f"Error processing student data: {e}")
        
        # Update the session's studentsinvited field by appending new IDs
        session.studentsinvited.extend(new_students)  # Append new student IDs to the existing list
        session.save()  # Save the session with the updated studentsinvited list
        # Prepare and send the email to the students
        subject = f"Invitation to Join: {session.Session_Topic} Session"
        message = f"""
        Hello,

        You have been registered for the session: {session.Session_Topic}.
        Details are as follows:
        Date: {session.Date}
        Time: {session.Start_Time}
        Conducted by: {session.conductedby}
        Meet Link: {session.meetlink}

        Regards,
        Exskilence Upskilling Program
        """
        from_email = settings.EMAIL_HOST_USER
        send_session_email(subject, message, from_email, recipient_emails)
        student_count = len(new_students)
        success_message = f"{student_count} students have been successfully added to the session: {sessiontopic}"
        return JsonResponse({'message': success_message}, status=201)    
    except Session.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def create_session(request):
    data = json.loads(request.body)
    
    try:
        max_id = Session.objects.aggregate(Max('id'))['id__max']
        new_id = (max_id or 0) + 1
        
        session = Session.objects.create(
            id=new_id,
            Session_Topic=data['Session_Topic'],
            Date=data['Date'],
            Start_Time=data['Start_Time'],
            conductedby=data['conductedby'],
            meetlink=data['meetlink'],
            Colleges=data['Colleges'],
            Branches=data['Branches']
        )
        recipient_emails = []
        for student_data in data['Students']:
            try:
                Student.objects.create(
                    session=session,
                    stuId=student_data['stuId'],
                    stuname=student_data['stuname'],
                    gender=student_data['gender'],
                    phonenumber=student_data['phonenumber'],
                    branch=student_data['branch'],
                    collegeName=student_data['collegeName'],
                    email=student_data['email']
                )
                recipient_emails.append(student_data['email'])
            except Exception as e:
                print(f"Error creating student: {e}")
        subject = f"Details for the {session.Session_Topic} session"
        message = f"""
        Hello,

        You have been registered for the session: {session.Session_Topic}.
        Details are as follows:
        Date: {session.Date}
        Time: {session.Start_Time}
        Conducted by: {session.conductedby}
        Meet Link: {session.meetlink}

        Regards,
        Your Team
        """
        from_email = settings.EMAIL_HOST_USER

        send_session_email(subject, message, from_email, recipient_emails)
        
        return JsonResponse({'message': 'Session created and emails sent successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
def send_session_email(subject, message, from_email, recipient_list):
    
    context = ssl.create_default_context(cafile=certifi.where())

    try:
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.ehlo()  
            server.starttls(context=context) 
            server.ehlo()  
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

            email = EmailMessage(subject, message, from_email, recipient_list)

            for recipient in recipient_list:
                server.sendmail(from_email, recipient, email.message().as_string())
        print("Emails sent successfully!")
    except Exception as e:
        print(f"Failed to send emails: {e}")

@csrf_exempt
@require_http_methods(["GET"])
def get_all_sessions(request):
    sessions = Session.objects.all()
    session_data = []
    for session in sessions:
        session_data.append({
            'id': session.id,
            'Session_Topic': session.Session_Topic,
            'Date': session.Date.strftime('%Y-%m-%d'),
            'Start_Time': session.Start_Time,
            'conductedby': session.conductedby,
            'meetlink': session.meetlink,
            'hasEnded': session.ended,
            'videoLink': session.videoLink,  # Added videoLink
            'studentsinvited': session.studentsinvited  # Added studentsinvited
        })
    return JsonResponse(session_data, safe=False)


@csrf_exempt
@require_http_methods(["GET"])
def get_session_by_id(request, session_id):
    try:
        session = Session.objects.get(id=session_id)
        
        # Assuming 'Student' is a related model and you want to exclude the 'id' field
        student_fields = [field.name for field in session.students.model._meta.fields if field.name != 'id']
        
        session_data = {
            'id': session.id,
            'Session_Topic': session.Session_Topic,
            'Date': session.Date.strftime('%Y-%m-%d'),
            'Start_Time': session.Start_Time,
            'conductedby': session.conductedby,
            'meetlink': session.meetlink,
            'Colleges': session.Colleges,
            'Branches': session.Branches,
            'hasEnded':session.ended,
            
            # Fetch students and exclude 'id' by specifying other fields explicitly
            'Students': list(session.students.values(*student_fields))
        }
        return JsonResponse(session_data, safe=False)
    except Session.DoesNotExist:
        return JsonResponse({'error': 'Session does not exist'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def update_video_link(request):
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        video_link = data.get('videoLink')
        
        if not session_id or not video_link:
            return JsonResponse({'error': 'Both session_id and videoLink are required'}, status=400)
        
        # Fetch the session by ID
        session = Session.objects.get(id=session_id)
        
        # Update the videoLink field
        session.videoLink = video_link
        session.save()

        return JsonResponse({'message': 'Video link updated successfully'}, status=200)
    
    except Session.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)