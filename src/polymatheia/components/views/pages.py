from django.http import *
from django.shortcuts import *
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from polymatheia.components.forms import *
from polymatheia.components.views.common import *
import json, requests
from datetime import datetime

def index(request):
    if request.session['user']:
        api_ip = settings.API_IP
        udata = (request.session['user'], request.session['pw'])
        user = request.session['uinfo']
        ucourses = request.session['courses']
        courses = []
        for course in ucourses:
            course_data = {'course-id':[course['course_id']]}
            cobj = requests.get(api_ip+'course/view', 
                    json=course_data, auth=udata, verify=False)
            c = (cobj.json() if cobj.status_code == 200 else [])
            a_obj = requests.get(api_ip+'assignment/view', 
                    json=course_data, auth=udata, verify=False)
            assign = (a_obj.json() if a_obj.status_code == 200 else [])
            upcoming = []
            for a in assign:
                end_time = datetime.strptime(a['end_date'], '%m/%d/%y %H:%M:%S')
                if end_time > datetime.now():
                    upcoming.append(a)
            if c != []:
                c[0]['upcoming'] = upcoming
                courses.append(c[0])
        return render_to_response('index.html', {'user':user,'courses':courses})
    return HttpResponseRedirect('/login')

def about(request):
	return render_to_response('about.html')


