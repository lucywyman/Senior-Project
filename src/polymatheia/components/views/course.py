from django.http import HttpResponse
from polymatheia.components.models import Student
import json

def courses(request):
    """
    Returns a list of courses the student or teacher is enrolled in.
    """
    courses = # 

    data = {
            'courses': courses        
            }
    return HttpResponse(json.dumps(data), content_type='application/json')
