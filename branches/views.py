from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Branch
import json

@csrf_exempt
@require_http_methods(["POST"])
def create_branch(request):
    data = json.loads(request.body)
    try:
        branch_name = data['branchname']
        branch = Branch.objects.create(branchname=branch_name)
        return JsonResponse({'message': 'Branch created successfully', 'id': branch.id}, status=201)
    except KeyError:
        return JsonResponse({'error': 'Branch name not provided'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def list_branches(request):
    try:
        branches = Branch.objects.all()
        branch_list = [{'id': branch.id, 'branchname': branch.branchname} for branch in branches]
        # Return the list of branches directly without the extra object wrapping
        return JsonResponse(branch_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
