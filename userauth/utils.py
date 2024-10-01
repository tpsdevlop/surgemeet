from oauth2client import client
import urllib
import requests
import json
from oauth2client.client import OAuth2Credentials
from django.core.exceptions import ObjectDoesNotExist
from .models import UserActivity, UserLogin

# import jwt
def get_id_token_with_code_method_1(code):
    credentials = client.credentials_from_clientsecrets_and_code(
        'client_secret.json',
        ['email','profile'],
        code
    )
    print(credentials.id_token)
    return credentials.id_token

# def get_id_token_with_code_method_2(code):
#     token_enpoint = "https://oauth2.googleapis.com/token"
#     payload ={
#         'code':code,
#         'client_id':'770296241282-5ubc9qv97gb8rgh9i74t0g1879v8qo36.apps.googleusercontent.com',
#         'client_secret':'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',
#         'grant_type': 'authorization_code',
#         'redirect_uri':"postmessage"
#     }

#     body = urllib.parse.urlencode(payload)
#     headers = {
#         'content-type':'application/x-www-form-urlencoded'
#     }


#     response = requests.post(token_enpoint,data= body,headers=headers)
#     print(response.json())
#     if response.ok:
#         id_token = response.json()['id_token']
#         return jwt.decode(id_token, options={"verify_signature": False})
#     else:
#         print(response.json())
#         return None

def get_id_token_with_code_method_2(code):
    CLIENT_SECRET_FILE = 'client_secret.json'

    # Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_clientsecrets_and_code(
        CLIENT_SECRET_FILE,
       ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/meetings.space.created',
          'https://www.googleapis.com/auth/userinfo.email', 
          'https://www.googleapis.com/auth/userinfo.profile',
          'openid'],
        code
    )
    # print(credittodic(credentials))
    print(credentials.to_json())
    return credentials


def credittodic(credentials):
    if isinstance(credentials, OAuth2Credentials):
        return {
            'access_token': credentials.access_token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'id_token': credentials.id_token,
            'scopes': credentials.scopes,
            'token_expiry': credentials.token_expiry.isoformat() if credentials.token_expiry else None,
            'revoke_uri': credentials.revoke_uri,
            'token_response': credentials.token_response,
            'user_agent': credentials.user_agent
        }
    return None

def clear_user_data(user_email):
    try:
        user_login = UserLogin.objects.get(email=user_email)
        user_login.delete()
        
        try:
            user = UserLogin.objects.get(email=user_email)
            UserActivity.objects.filter(user=user).delete()
        except ObjectDoesNotExist:
            print(f"User with email {user_email} does not exist. Skipping activity deletion.")
        return {"message": "User login data cleared successfully", "status": "success"}
    except UserLogin.DoesNotExist:
        return {"message": "User login data not found", "status": "failure"}







