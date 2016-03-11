from django.http import *
from django.shortcuts import *
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from polymatheia.components.forms import *
import datetime, json, requests

def index(request):
    api_ip = settings.API_IP
    user_data = {'student':['hennign']}
    userobj = requests.get(api_ip+'student/view', json=user_data)
    user = userobj.json()
    for i in range(len(user)):
        user[i]['type'] = 'student'
    courses = []
    for course in user:
        course_data = {'course-id':[course['course_id']]}
        cobj = requests.get(api_ip+'course/view', json=course_data)
        c = cobj.json()
        aobj = requests.get(api_ip+'assignment/view')
        c[0]['assignments'] = aobj.json()
        courses.append(c[0])
    return render_to_response('index.html', {'n':datetime.datetime.now(), 'user':user[0], 'courses':courses})

def about(request):
	return render_to_response('about.html')


