# views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
import json

@csrf_exempt
def add_user(request):
    if request.method == 'POST':
        try:
            user_data = json.loads(request.body)
            user = User.objects.create(
                id=user_data['id'],
                email=user_data['email'],
                name=user_data['name']
            )
            return JsonResponse({'message': 'User created successfully', 'user_id': user.id}, status=201)
        except KeyError as e:
            return JsonResponse({'error': f'Missing required field: {e}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
  


def get_all_users(request):
    try:
        all_users = User.objects.all()
        all_users_data = list(all_users.values())
        return JsonResponse(all_users_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



