from django.urls import path
from .views import (
    send_meet_link, get_meeting_details, list_conferences,
    list_participants, list_all_participant_sessions,
    getParticipantsList, getParticipantsLog,
    get_live_details_session
)
from .extractionviews import *
from .sessionsview import * 
urlpatterns = [
    path('create_meet/<str:email>/', send_meet_link, name='meet_link'),
    path('meet_details/<str:meeting_code>/<str:email>/', get_meeting_details, name='meet_details'),
    path('list_conferences/<str:email>/', list_conferences, name='list_conferences'),
    path('conference/<str:conference_id>/participants/<str:email>/', list_participants, name='list_participants'),
    path('conference/<str:conference_id>/participant_sessions/<str:email>/', list_all_participant_sessions, name='list_all_participant_sessions'),
    path('get_participants_list/<str:meeting_code>/<str:instructorName>/<str:email>/', getParticipantsList, name='get_participants_list'),
    path('get_participants_log/<str:meeting_code>/<str:instructorName>/<str:email>/', getParticipantsLog, name='get_participants_log'),
    path('justtestting/',get_live_details_session,name='get_live_detials_session'),
    path('conference-ids/',get_conference_ids_by_meeting_link, name='conference_ids_by_meeting_link'),
    path('participant-sessions-by-link/', list_participant_sessions_by_meeting_link, name='participant_sessions_by_link'),
    path('get-participant-info/', get_all_participant_info_from_meeting_link, name='get_participant_info'),
    path('get-session-info/', get_session_and_participant_info, name='get_session_info'),
]
