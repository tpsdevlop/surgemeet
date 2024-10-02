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
from .models import UserToken
import pytz
from userauth.models import UserLogin
from dateutil import parser
from django.views.decorators.csrf import csrf_exempt




SCOPES = [
    'https://www.googleapis.com/auth/meetings.space.created',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid' 
]

# def authenticate_google(email):
#     creds = None
#     try:
#         logging.info("Attempting to load credentials from the database...")
#         user_token = UserToken.objects.get(pk=email)  # Replace with actual user's email
#         creds_data = user_token.token
#         creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
#         logging.info("Credentials loaded from the database.")

#         if creds and creds.expired and creds.refresh_token:
#             try:
#                 logging.info("Credentials expired. Attempting to refresh...")
#                 creds.refresh(Request())
#                 logging.info("Credentials refreshed successfully.")
#                 create_userToken(user_token.userEmail, creds.to_json())
#             except Exception as e:
#                 logging.error(f"Error refreshing credentials: {e}")
#                 creds = None
#     except UserToken.DoesNotExist:
#         logging.info("No credentials found in the database. Initiating authentication flow...")
#     except Exception as e:
#         logging.error(f"Error loading credentials from the database: {e}")
#         creds = None

#     if not creds or not creds.valid:
#         try:
#             logging.info("Starting authentication flow...")
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#             logging.info("Authentication successful, credentials obtained.")
#             service = build('oauth2', 'v2', credentials=creds)
#             user_info = service.userinfo().get().execute()
#             email = user_info.get('email')
#             logging.info(f"User email retrieved: {email}")

#             if not email:
#                 raise ValueError("Failed to retrieve user email.")
#             create_userToken(email, creds.to_json())
#             logging.info(f"Credentials saved to the database for {email}.")
#         except Exception as e:
#             logging.error(f"Error during authentication: {e}")

#     return creds

# def create_userToken(email, token_json):
#     try:
#         logging.info(f"Saving token to the database for {email}...")
#         token = json.loads(token_json)
#         userToken, created = UserToken.objects.update_or_create(
#             userEmail=email,
#             defaults={'token': token}
#         )
#         if created:
#             logging.info(f"Created new token record for {email}.")
#         else:
#             logging.info(f"Updated token record for {email}.")
#     except json.JSONDecodeError as e:
#         logging.error(f"Error decoding JSON token: {e}")
#     except Exception as e:
#         logging.error(f"Error saving token to the database: {e}")

# def get_userToken(email):
#     try:
#         logging.info(f"Fetching token from the database for {email}...")
#         userToken = UserToken.objects.get(pk=email)
#         logging.info("Token fetched successfully.")
#         return userToken.token
#     except UserToken.DoesNotExist:
#         logging.info("No token found in the database for this user.")
#         return None
#     except Exception as e:
#         logging.error(f"Error fetching token from the database: {e}")
#         return None
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
@require_GET
def send_meet_link(request,email):
    creds = get_token(email)
    try:
        client = meet_v2.SpacesServiceClient(credentials=creds)
        request = meet_v2.CreateSpaceRequest()
        response = client.create_space(request=request)
        meeting_uri = response.meeting_uri
        return HttpResponse(meeting_uri)
    except Exception as error:
        return HttpResponse(f'An error occurred: {error}')



@require_GET
def get_meeting_details(request, meeting_code,email):
    creds = get_token(email)
    try:
        client = meet_v2.SpacesServiceClient(credentials=creds)
        request = meet_v2.GetSpaceRequest(name=f'spaces/{meeting_code}')
        response = client.get_space(request=request)
        print(response)
        meeting_details = {
            'name': response.name,
            'meeting_code': meeting_code,
            'meeting_uri': response.meeting_uri,
            'other_attribute': getattr(response, 'other_attribute', 'N/A'),
        }
        return JsonResponse(meeting_details)
    except Exception as error:
        return HttpResponse(f'An error occurred: {error}')







def list_conferences(request,email):
    print(email)
    creds = get_token(email)
    if creds is None or not creds.valid:
        return HttpResponse("Failed to authenticate Google credentials or credentials are invalid.", content_type="text/plain")
    try:
        client = meet_v2.ConferenceRecordsServiceClient(credentials=creds)
        request_obj = meet_v2.ListConferenceRecordsRequest()
        page_result = client.list_conference_records(request=request_obj)
        raw_response = list(page_result) 
        print("Raw response:", raw_response)  

        if not raw_response:
            return HttpResponse("No conference records found for the authenticated user.", content_type="text/plain")
        response_data = [str(response) for response in raw_response]
        response_text = "\n".join(response_data)
        return HttpResponse(response_text, content_type="text/plain")
    except Exception as error:
        return HttpResponse(f'An error occurred while listing conferences: {error}', content_type="text/plain")

@require_GET
def list_participants(request, conference_id,email):
    creds = get_token(email)
    try:
        client = meet_v2.ConferenceRecordsServiceClient(credentials=creds)
        request = meet_v2.ListParticipantsRequest(parent=f'conferenceRecords/{conference_id}')
        page_result = client.list_participants(request=request)
        response_data = [str(response) for response in page_result]
        response_text = "\n".join(response_data)
        return HttpResponse(response_text, content_type="text/plain")
    except Exception as error:
        return HttpResponse(f'An error occurred: {error}')

@require_GET
def list_all_participant_sessions(request, conference_id,email):
    creds = get_token(email)
    try:
        client = meet_v2.ConferenceRecordsServiceClient(credentials=creds)
        participants_request = meet_v2.ListParticipantsRequest(parent=f'conferenceRecords/{conference_id}')
        participants_result = client.list_participants(request=participants_request)
        participant_names = {participant.name.split('/')[-1]: participant.signedin_user.display_name for participant in participants_result}
        sessions_data = []
        for participant_id, display_name in participant_names.items():
            sessions_request = meet_v2.ListParticipantSessionsRequest(parent=f'conferenceRecords/{conference_id}/participants/{participant_id}')
            sessions_result = client.list_participant_sessions(request=sessions_request)
            for session in sessions_result:
                sessions_data.append({
                    'participant_id': participant_id,
                    'display_name': display_name,
                    'session_start_time': session.start_time,
                    'session_end_time': session.end_time
                })
        return JsonResponse(sessions_data, safe=False)
    except Exception as error:
        return HttpResponse(f'An error occurred: {error}')

from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
import json

@csrf_exempt
@require_POST
def get_live_details_session(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        meetingcode = data.get('meetingcode')
        instructorName = data.get('instructorName')

        creds = get_token(email)
        client = meet_v2.SpacesServiceClient(credentials=creds)
        space_request = meet_v2.GetSpaceRequest(name=f'spaces/{meetingcode}')
        response = client.get_space(request=space_request)
        print("Response of Google Meet details:", response)

        meeting_details = {
            'name': response.name,
            'meeting_code': meetingcode,
            'meeting_uri': response.meeting_uri,
            'other_attribute': getattr(response, 'other_attribute', 'N/A'),
        }

        active_conference_id = response.active_conference.conference_record
        if active_conference_id:
            try:
                client = meet_v2.ConferenceRecordsServiceClient(credentials=creds)
                participant_request = meet_v2.ListParticipantsRequest(parent=f'{active_conference_id}')
                page_result = client.list_participants(request=participant_request)
                print(page_result)
                
                members_of_meet = {}
                participants = []
                for i in page_result:
                    joined_time = convert_to_ist(i.earliest_start_time)
                    exit_time = convert_to_ist(i.latest_end_time) if hasattr(i, 'latest_end_time') else None
                    if exit_time == "N/A":
                        status = "Active"
                        exit_time = ""
                    else:
                        status = "Inactive"
                    
                    if i.signedin_user.display_name == instructorName:
                        instdic = {
                            "display_name": str(i.signedin_user.display_name),
                            "joinedTime": joined_time,
                            "exitTime": exit_time,
                            "status": status
                        }
                        members_of_meet["instructor"] = instdic
                    else:
                        participant_info = {
                            "display_name": str(i.signedin_user.display_name),
                            "joinedTime": joined_time,
                            "exitTime": exit_time,
                            "status": status
                        }
                        participants.append(participant_info)
                
                members_of_meet["participants"] = participants
                return JsonResponse(members_of_meet)

            except Exception as error:
                return JsonResponse({"error": str(error)})
        else:
            return HttpResponse("This is not a live conference, so details cannot be fetched.", content_type="text/plain", status=400)

    except Exception as error:
        return HttpResponse(f"An error occurred: {error}", content_type="text/plain")




@require_GET
def getParticipantsList(request, meeting_code, instructorName,email):
    creds = get_token(email)
    try:
        client = meet_v2.SpacesServiceClient(credentials=creds)
        space_request = meet_v2.GetSpaceRequest(name=f'spaces/{meeting_code}')
        space_response = client.get_space(request=space_request)
        space_name_of_the_meeting = space_response.name.split('/')[1]
        conference_list = attendenceInstPartInfo(space_name_of_the_meeting, instructorName,email)
        return JsonResponse(conference_list, safe=False)
    except Exception as error:
        return JsonResponse({'error': str(error)})

def attendenceInstPartInfo(nameOfMeeting, instructorName,email):
    creds = get_token(email)
    try:
        conference_id = getConferenceIdByName(creds, nameOfMeeting)
        if conference_id:
            client = meet_v2.ConferenceRecordsServiceClient(credentials=creds)
            request = meet_v2.ListParticipantsRequest(parent=f'conferenceRecords/{conference_id}')
            page_result = client.list_participants(request=request)
            members_of_meet = {}
            participants = []
            for i in page_result:
                joined_time = convert_to_ist(i.earliest_start_time)
                exit_time = convert_to_ist(i.latest_end_time)
                if i.signedin_user.display_name == instructorName:
                    instdic = {
                        "display_name": str(i.signedin_user.display_name),
                        "joinedTime": joined_time,
                        "exitTime": exit_time
                    }
                    members_of_meet["instructor"] = instdic
                else:
                    participant_info = {
                        "display_name": str(i.signedin_user.display_name),
                        "joinedTime": joined_time,
                        "exitTime": exit_time
                    }
                    participants.append(participant_info)
            members_of_meet["participants"] = participants
            return members_of_meet
        return {"participants": []}
    except Exception as error:
        return {"error": str(error)}

def getConferenceIdByName(creds, nameOfMeeting):
    client = meet_v2.ConferenceRecordsServiceClient(credentials=creds)
    request = meet_v2.ListConferenceRecordsRequest()
    page_result = client.list_conference_records(request=request)
    for response in page_result:
        if nameOfMeeting in str(response.space):
            return str(response.name).split('/')[1]
    return None

def convert_to_ist(timestamp):
    if not timestamp:
        return "N/A"
    utc_time = datetime.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S.%f%z")
    ist_timezone = pytz.timezone("Asia/Kolkata")
    ist_time = utc_time.astimezone(ist_timezone)
    return ist_time.strftime("%Y-%m-%d %H:%M:%S %Z%z")

def calculate_duration(start_time: str, end_time: str):
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    duration = end - start
    minutes = duration.total_seconds() / 60
    return int(minutes)

def getAllparticipantInfo(conference_id, instName,email):
    creds = get_token(email)
    try:
        client = meet_v2.ConferenceRecordsServiceClient(credentials=creds)
        participants_request = meet_v2.ListParticipantsRequest(parent=f'conferenceRecords/{conference_id}')
        participants_result = client.list_participants(request=participants_request)
        participant_info = []
        for participant in participants_result:
            if participant.signedin_user.display_name != instName:
                participant_id = participant.name.split('/')[-1]
                display_name = participant.signedin_user.display_name
                sessions_request = meet_v2.ListParticipantSessionsRequest(parent=f'conferenceRecords/{conference_id}/participants/{participant_id}')
                sessions_result = client.list_participant_sessions(request=sessions_request)
                session_logs = []
                total_attended_time = 0
                for session in sessions_result:
                    start_time = convert_to_ist(session.start_time)
                    end_time = convert_to_ist(session.end_time)
                    session_duration = calculate_duration(str(session.start_time), str(session.end_time))
                    total_attended_time += session_duration
                    session_logs.append({
                        'session_start_time': start_time,
                        'session_end_time': end_time
                    })
                participant_info.append({
                    'display_name': display_name,
                    'attendedTime': f"{total_attended_time} mins",
                    'log': session_logs
                })
        return {"participantInfo": participant_info}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"participantInfo": []}

@require_GET
def getParticipantsLog(request, meeting_code, instructorName,email):
    creds = get_token(email)
    if not creds:
        return JsonResponse({'error': 'Google authentication failed'}, status=500)
    try:
        client = meet_v2.SpacesServiceClient(credentials=creds)
        space_request = meet_v2.GetSpaceRequest(name=f'spaces/{meeting_code}')
        space_response = client.get_space(request=space_request)
        space_name_of_the_meeting = space_response.name.split('/')[1]
        conference_id = getConferenceIdByName(creds, space_name_of_the_meeting)
        if not conference_id:
            return JsonResponse({'error': 'No conference ID found'}, status=404)
        session_details = sessionDetials(instructorName, conference_id,email)
        participant_info = getAllparticipantInfo(conference_id, instructorName,email)
        final_resp = {
            "session_details": session_details,
            "participantInfo": participant_info
        }
        return JsonResponse(final_resp)
    except Exception as e:
        return JsonResponse({'error': f'Space not found: {e}'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {e}'}, status=500)

def sessionDetials(instructorName, conference_id,email):
    creds = get_token(email)
    try:
        client = meet_v2.ConferenceRecordsServiceClient(credentials=creds)
        request = meet_v2.ListParticipantsRequest(parent=f'conferenceRecords/{conference_id}')
        page_result = client.list_participants(request=request)
        SessStartedbyInst = ""
        SessEndedByInst = ""
        Sessiontotalduration = 0
        for response in page_result:
            if response.signedin_user.display_name == instructorName:
                SessStartedbyInst = convert_to_ist(response.earliest_start_time)
                SessEndedByInst = convert_to_ist(response.latest_end_time)
                Sessiontotalduration = calculate_duration(str(response.earliest_start_time), str(response.latest_end_time))
        return {"SessStartedbyInst": SessStartedbyInst, "SessEndedByInst": SessEndedByInst, "Sessiontotalduration": Sessiontotalduration}
    except Exception as error:
        return {"error": str(error)}
    return 0