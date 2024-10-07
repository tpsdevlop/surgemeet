from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Log, Session,Participant
@csrf_exempt
def get_session_and_participant_info(request):
    if request.method == 'POST':
        try:
            # Step 1: Parse the input data
            data = json.loads(request.body)
            session_id = data.get('session_id')  # Extract session ID from the request

            if not session_id:
                return JsonResponse({'error': 'session_id is required.'}, status=400)

            # Step 2: Get the session details based on session ID
            try:
                session = Session.objects.get(session_id=session_id)
            except Session.DoesNotExist:
                return JsonResponse({'error': 'Session not found.'}, status=404)

            # Step 3: Get the participants for the session
            participants = Participant.objects.filter(session=session)

            # Step 4: Create the response data
            session_info = {
                'sessionId': session.session_id,
                'email': session.email,
                'inst_name': session.inst_name,
                'session_duration': session.session_duration,
            }

            participant_info = []
            for participant in participants:
                # Get participant logs
                logs = Log.objects.filter(session_id=session.session_id, student_id=participant.student_id)

                # Collect log details
                session_logs = [{
                    'session_start_time': log.session_start_time,
                    'session_end_time': log.session_end_time
                } for log in logs]

                # Append participant info
                participant_info.append({
                    'student_id': participant.student_id,
                    'display_name': participant.display_name,
                    'attendedTime': participant.attended_time,
                    'log': session_logs
                })

            # Step 5: Build the final response object
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