from django.http import *
from django.shortcuts import *
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from polymatheia.components.forms import *
from polymatheia.components.views.common import *
import datetime, json, requests

def index(request):
    if request.session.get('user'):
        api_ip = settings.API_IP
        udata = (request.session.get('user'), request.session.get('pw'))
        user = get_courses(request)
        courses = []
        for course in user:
            course_data = {'course-id':[course['course_id']]}
            cobj = requests.get(api_ip+'course/view', 
                    json=course_data, auth=udata, verify=False)
            c = (cobj.json() if cobj.status_code == 200 else [])
            aobj = requests.get(api_ip+'assignment/view', 
                    json=course_data, auth=udata, verify=False)
            c[0]['assignments'] = (aobj.json() if aobj.status_code == 200 else [])
            courses.append(c[0])
        return render_to_response('index.html', {'n':datetime.datetime.now(), 'user':user[0], 'courses':courses})
    else:
        return HttpResponseRedirect('/login')

def about(request):
	return render_to_response('about.html')


