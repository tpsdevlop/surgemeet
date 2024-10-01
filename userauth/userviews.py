from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
from .models import UserDetails

@csrf_exempt
def add_user_details(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user = UserDetails(
                userID=data.get('userID'),
                email=data.get('email'),
                category=data.get('category'),
                expiry_date=data.get('expiry_date'),
                status=data.get('status')
            )
            user.save()
            return JsonResponse({"message": "User details added successfully!"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
from django.http import JsonResponse
from .models import UserDetails

def get_user_details(request):
    if request.method == 'GET':
        try:
            users = UserDetails.objects.all().values('userID', 'email', 'category', 'expiry_date', 'status', 'register_date')
            users_list = list(users)
            return JsonResponse(users_list, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
