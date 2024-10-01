from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import College
import json

@csrf_exempt
@require_http_methods(["POST"])
def create_college(request):
    data = json.loads(request.body)
    try:
        college_name = data['name']
        college = College.objects.create(name=college_name)
        return JsonResponse({'message': 'College created successfully', 'id': str(college.id)}, status=201)
    except KeyError:
        return JsonResponse({'error': 'College name not provided'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def update_college(request, college_id):
    data = json.loads(request.body)
    try:
        college_name = data['name']
        college = College.objects.get(id=college_id)
        college.name = college_name
        college.save()
        return JsonResponse({'message': 'College updated successfully'}, status=200)
    except College.DoesNotExist:
        return JsonResponse({'error': 'College not found'}, status=404)
    except KeyError:
        return JsonResponse({'error': 'College name not provided'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def list_colleges(request):
    try:
        colleges = College.objects.all()
        college_list = [{'name': college.name} for college in colleges]
        return JsonResponse(college_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
