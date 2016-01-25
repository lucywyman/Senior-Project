from django.http import (HttpResponse,
        HttpResponseNotFound)
from polymatheia.components.models import Course
import json
from .serializer import FreshSerializer

def course_list(request):
    """
    */course/*

    Returns a list of the courses a student is enrolled in, or the courses
    an admin is teaching
    """
        error = { 
                'status': False,
                'name': None,
                'text': None,
                'level': None,
                'debug': None
                }   

        serializer = FreshSerializer()
        queryset = Course.objects.all()

        if not queryset:
            error = { 
                    "status": True,
                    "name": "No Products",
                    "text": "No Products found",
                    "level": "Information",
                    "debug": ""
                    }

        data = { 
                "products": json.loads(
                    serializer.serialize(
                        queryset,
                        use_natural_foreign_keys=True
                        )
                    ),
                "error": error
                }

        return HttpResponse(json.dumps(data), content_type="application/json")

def course_details(request):
    """
    */course/<id>*

    Returns a list of course data, including when it is, course number,
    etc.
    """
    data = {}

        try:
            product = Product.objects.get(id=id)
        except Exception as e:
            data['error'] = {
                    'status': True,
                    'name': 'Product Not Found',
                    'text': 'Product id %s was not found.' % id,
                    'level': 'Error',
                    'debug': '{0}: {1}'.format(type(e).__name__, str(e))
                    }
            return HttpResponseNotFound(
                    json.dumps(data),
                    content_type="application/json"
                    )

        error = {
                'status': False,
                'name': None,
                'text': None,
                'level': None,
                'debug': None
                }

        serializer = FreshSerializer()
        data = json.loads(
                serializer.serialize(
                    [product],
                    use_natural_foreign_keys=True
                    )[1:-1]
                )

        data['error'] = error

        return HttpResponse(json.dumps(data), content_type="application/json")

def course_assignment(request):
    """
    */course/assignments/*

    Return a list of assignments for the course
    """

