from django.http import HttpResponse, JsonResponse
from google.auth.credentials import Credentials
import asyncio
from datetime import datetime, timedelta
import json
import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.apps import meet_v2
from django.core.exceptions import ObjectDoesNotExist
from googleapiclient.discovery import build
import os
from .models import Log, Participant, Session, UserToken
from datetime import datetime, timezone, timedelta

import pytz
from userauth.models import UserLogin
from dateutil import parser
from django.views.decorators.csrf import csrf_exempt 
from student.models import *
def get_token(email):
    user_token = UserLogin.objects.get(email=email)
    access_token = user_token.token
    token_expiry = parser.isoparse(access_token.get('token_expiry')) if access_token.get('token_expiry') else None

    creds = Credentials(
        token=access_token.get('access_token'),
        refresh_token=access_token.get('refresh_token'),
        id_token=access_token.get('id_token'),
        token_uri=access_token.get('token_uri'),
        client_id=access_token.get('client_id'),
        client_secret=access_token.get('client_secret'),
        scopes=access_token.get('scopes'),
        expiry=token_expiry,
    )

    return creds
@csrf_exempt
def get_conference_ids_by_meeting_link(request):
    if request.method == 'POST':
        try:
            print("POST request received")
            data = json.loads(request.body)
            print(f"Request data: {data}")
            meeting_link = data.get('meeting_link')
            email = data.get('email')
            if not meeting_link or not email:
                print("Meeting link or email missing")
                return JsonResponse({'error': 'Both meeting_link and email are required.'}, status=400)
            meeting_code = meeting_link.split('/')[-1]  
            print(f"Extracted meeting code: {meeting_code}")
            creds = get_token(email)
            if creds is None or not creds.valid:
                print("Invalid or missing credentials")
                return JsonResponse({'error': 'Failed to authenticate Google credentials or credentials are invalid.'}, status=401)
            client = meet_v2.SpacesServiceClient(credentials=creds)
            print("SpacesServiceClient initialized")
            space_request = meet_v2.GetSpaceRequest(name=f'spaces/{meeting_code}')
            space_response = client.get_space(request=space_request)
            space_name = space_response.name
            print(f"Space name retrieved: {space_name}")
            conference_client = meet_v2.ConferenceRecordsServiceClient(credentials=creds)
            print("ConferenceRecordsServiceClient initialized")
            request_obj = meet_v2.ListConferenceRecordsRequest()
            page_result = conference_client.list_conference_records(request=request_obj)
            print("Conference records retrieved")
            conference_ids = [
                record.name for record in page_result if record.space == space_name
            ]
            print(f"Extracted matching conference IDs: {conference_ids}")
            return JsonResponse({'conference_ids': conference_ids})
        except json.JSONDecodeError:
            print("JSONDecodeError: Invalid JSON body")
            return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        except Exception as error:
            print(f"An error occurred: {error}")
            return JsonResponse({'error': f"An error occurred: {error}"}, status=500)
    else:
        print("Invalid request method, only POST is allowed")
        return JsonResponse({'error': 'POST method required.'}, status=405)
# Main method to list participant sessions based on the meeting link
@csrf_exempt
def list_participant_sessions_by_meeting_link(request):
    if request.method == 'POST':
        try:
            # Step 1: Parse the input data
            data = json.loads(request.body)
            meeting_link = data.get('meeting_link')
            email = data.get('email')
            sessionid = data.get('session_id')

            if not meeting_link or not email:
                return JsonResponse({'error': 'Both meeting_link and email are required.'}, status=400)

            meeting_code = meeting_link.split('/')[-1]  # Extract the meeting code from the link
            creds = get_token(email)
            if creds is None or not creds.valid:
                return JsonResponse({'error': 'Failed to authenticate Google credentials or credentials are invalid.'}, status=401)

            # Step 2: Get the space name using the meeting code
            client = meet_v2.SpacesServiceClient(credentials=creds)
            space_request = meet_v2.GetSpaceRequest(name=f'spaces/{meeting_code}')
            space_response = client.get_space(request=space_request)
            space_name = space_response.name

            # Step 3: List conferences associated with the space
            conference_client = meet_v2.ConferenceRecordsServiceClient(credentials=creds)
            request_obj = meet_v2.ListConferenceRecordsRequest()
            page_result = conference_client.list_conference_records(request=request_obj)

            # Filter conference records that match the space name
            conference_ids = [record.name.split('/')[-1] for record in page_result if record.space == space_name]
            if not conference_ids:
                return JsonResponse({'error': 'No conferences found for the provided meeting link.'}, status=404)

            # Step 4: Load all student data into a dictionary
            students = Student.objects.all()
            student_dict = {student.stuname.lower(): student.stuId for student in students}  # Mapping stuname to stuId (case-insensitive)

            # Step 5: Retrieve participant sessions and match with student data
            sessions_data = []
            for conference_id in conference_ids:
                participants_request = meet_v2.ListParticipantsRequest(parent=f'conferenceRecords/{conference_id}')
                participants_result = conference_client.list_participants(request=participants_request)
                participant_names = {participant.name.split('/')[-1]: participant.signedin_user.display_name for participant in participants_result}

                for participant_id, display_name in participant_names.items():
                    sessions_request = meet_v2.ListParticipantSessionsRequest(parent=f'conferenceRecords/{conference_id}/participants/{participant_id}')
                    sessions_result = conference_client.list_participant_sessions(request=sessions_request)

                    # Step 6: Find matching student by display_name
                    stu_id = student_dict.get(display_name.lower())  # Get student ID if a match is found, else None

                    for session in sessions_result:
                        session_info = {
                            'conference_id': conference_id,
                            'participant_id': participant_id,
                            'display_name': display_name,
                            'session_start_time': session.start_time,
                            'session_end_time': session.end_time,
                            'stuid': stu_id 
                        }
                        sessions_data.append(session_info)

            return JsonResponse(sessions_data, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        except Exception as error:
            return JsonResponse({'error': f'An error occurred: {error}'}, status=500)
    else:
        return JsonResponse({'error': 'POST method required.'}, status=405)


# Convert a timestamp to IST (Indian Standard Time)
def convert_to_ist(utc_time):
    utc_dt = parser.isoparse(utc_time)  # Use dateutil to parse the datetime
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = utc_dt + ist_offset
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')

# Calculate duration between two times
def calculate_duration(start_time, end_time):
    start_dt = parser.isoparse(start_time)  # Use dateutil to parse the datetime
    end_dt = parser.isoparse(end_time)  # Use dateutil to parse the datetime
    duration = end_dt - start_dt
    return int(duration.total_seconds() // 60)  # Return duration in minutes
@csrf_exempt
def get_all_participant_info_from_meeting_link(request):
    if request.method == 'POST':
        try:
            # Step 1: Parse the input data
            data = json.loads(request.body)
            # print(data)
            meeting_link = data.get('meeting_link')
            email = data.get('email')
            inst_name = data.get('name')
            session_id = data.get('session_id')  # Capture session ID from request
            print("this is post bodedy+++++++++++++++++++.\t",meeting_link,email,inst_name,session_id)
            if not meeting_link or not email:
                return JsonResponse({'error': 'Both meeting_link and email are required.'}, status=400)

            meeting_code = meeting_link.split('/')[-1]  # Extract the meeting code from the link
            creds = get_token(email)
            if creds is None or not creds.valid:
                return JsonResponse({'error': 'Failed to authenticate Google credentials or credentials are invalid.'}, status=401)

            # Step 2: Get the space name using the meeting code
            client = meet_v2.SpacesServiceClient(credentials=creds)
            space_request = meet_v2.GetSpaceRequest(name=f'spaces/{meeting_code}')
            space_response = client.get_space(request=space_request)
            space_name = space_response.name

            # Step 3: List conferences associated with the space
            conference_client = meet_v2.ConferenceRecordsServiceClient(credentials=creds)
            request_obj = meet_v2.ListConferenceRecordsRequest()
            page_result = conference_client.list_conference_records(request=request_obj)

            # Filter conference records that match the space name
            conference_ids = [record.name.split('/')[-1] for record in page_result if record.space == space_name]
            if not conference_ids:
                return JsonResponse({'error': 'No conferences found for the provided meeting link.'}, status=404)

            # Initialize session info
            session_info = {
                "sessionInfo": [],
                "participantInfo": []
            }

            # Step 4: Get participant info for each conference
            for conference_id in conference_ids:
                # Get participant info including instructor
                participant_info = get_all_participant_info_method(conference_id, email, creds, inst_name, session_id)
                # print(participant_info)
                session_duration = 0

                # Find the instructor's info and calculate the duration
                for participant in participant_info['participantInfo']:
                    # print("trying to print name\t"+participant['display_name']+"another apporach"+participant[2])
                    if participant['display_name'] == inst_name:
                        session_duration = participant['attendedTime']  # Get instructor's attended time
                        break

                # Convert attended time to minutes for comparison
                # if session_duration and "mins" in session_duration:
                #     duration_minutes = int(session_duration.replace(" mins", ""))
                # else:
                #     duration_minutes = 0

                # Only include sessions with a duration greater than 0 minutes
                if session_duration > 0:
                    session_detail = {
                        "sessionId": session_id,  # Use session ID from request
                        "email": email,
                        "inst_name": inst_name,
                        "session_duration": session_duration  # Use the instructor's duration
                    }
                    session_info["sessionInfo"].append(session_detail)

                session_info["participantInfo"].extend(participant_info['participantInfo'])

            # Save the session and participant info to the database
            save_session_info(session_info)

            return JsonResponse(session_info, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return JsonResponse({'error': f'An error occurred: {e}'}, status=500)
    else:
        return JsonResponse({'error': 'POST method required.'}, status=405)
def get_all_participant_info_method(conference_id, email, creds, inst_name, session_id):
    client = meet_v2.ConferenceRecordsServiceClient(credentials=creds)
    participants_request = meet_v2.ListParticipantsRequest(parent=f'conferenceRecords/{conference_id}')
    participants_result = client.list_participants(request=participants_request)

    participant_info = []
    for participant in participants_result:
        display_name = participant.signedin_user.display_name        
        # Retrieve the student ID from the database based on display name
        try:
            student = Student.objects.get(stuname=display_name)  # Match on student name
            student_id = student.stuId  # Assuming 'stuId' is the student ID field
        except Student.DoesNotExist:
            student_id = "0000"  # Handle the case where the student is not found

        participant_id = participant.name.split('/')[-1]
        sessions_request = meet_v2.ListParticipantSessionsRequest(parent=f'conferenceRecords/{conference_id}/participants/{participant_id}')
        sessions_result = client.list_participant_sessions(request=sessions_request)

        session_logs = []
        total_attended_time = 0
        
        for session in sessions_result:
            # Convert and calculate times
            start_time = convert_to_ist(session.start_time.isoformat())  # Convert to ISO format string
            end_time = convert_to_ist(session.end_time.isoformat())  # Convert to ISO format string
            session_duration = calculate_duration(start_time, end_time)  # This should return the duration in minutes
            total_attended_time += session_duration
            
            # Log session times
            session_logs.append({
                'session_start_time': start_time,
                'session_end_time': end_time
            })

        # Append participant info with student ID and the session ID from the outer function
        participant_info.append({
            'student_id': student_id,
            'session_id': session_id, 
            'display_name': display_name,
            'attendedTime': total_attended_time,  # Store the raw numerical value of attended time in minutes
            'log': session_logs
        })

    return {"participantInfo": participant_info}

def save_session_info(session_info):
    # Loop through each session in session_info
    for session_detail in session_info["sessionInfo"]:
        # Create a new session object
        session = Session(
            session_id=session_detail["sessionId"],  # Use the session ID from the request
            email=session_detail["email"],
            inst_name=session_detail["inst_name"],
            session_duration=session_detail["session_duration"]
        )
        session.save()  # Save the session to the database

        # print(f"Session saved with ID: {session.session_id}")  # Debugging line

        # Loop through participants and save their information
        for participant in session_info["participantInfo"]:
            participant_instance = Participant(
                session=session,  # Link to the session
                student_id=participant.get("student_id"),  # Include student ID
                display_name=participant["display_name"],
                attended_time=participant["attendedTime"]
            )
            participant_instance.save()  # Save participant to the database

            # print(f"Participant saved: {participant_instance.display_name}")  # Debugging line

            # Save logs for this participant with student ID and session ID
            for log in participant.get("log", []):
                log_instance = Log(
                    student_id=participant.get("student_id"),  # Store student ID
                    session_id=session_detail["sessionId"],  # Store session ID
                    session_start_time=log["session_start_time"],
                    session_end_time=log["session_end_time"]
                )
                log_instance.save()  # Save log to the database

                # print(f"Log saved for student: {log_instance.student_id}")  # Debugging line
