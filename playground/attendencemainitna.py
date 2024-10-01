import os
from django.http import JsonResponse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.apps import meet_v2

SCOPES = ['https://www.googleapis.com/auth/meetings.space.created']

def authenticate_google():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('gogolemeetplay\credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_meeting_details(meeting_code):
    creds = authenticate_google()

    try:
        client = meet_v2.SpacesServiceClient(credentials=creds)
        request = meet_v2.GetSpaceRequest(name=f'spaces/{meeting_code}')
        response = client.get_space(request=request)
        
        meeting_details = {
            'name': response.name,
            'meeting_code': meeting_code,
            'meeting_uri': response.meeting_uri,
            'other_attribute': getattr(response, 'other_attribute', 'N/A'),
        }
        
        return meeting_details
    except Exception as error:
        return f'An error occurred: {error}'

def get_conferencerid():
    print(get_meeting_details('vwg-twvt-nsh'))

if __name__ == "__main__":
    get_conferencerid()
