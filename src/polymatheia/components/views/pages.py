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
    if request.session.get('user'):
        api_ip = settings.API_IP
        udata = (request.session.get('user'), request.session.get('pw'))
        user_info = {request.session['type']:[request.session['user']]}
        if request.session['type'] == 'teacher':
            userobj = requests.get(api_ip+'course/view', json=user_info, 
                    auth=udata)
        else:
            userobj = requests.get(api_ip+'student/view', 
                    json=user_info, auth=udata)
        if userobj.status_code != 200:
            render_to_response('index.html', 
                    {'msg':'You\'re not registered for any courses yet!',
                        'user':{'student':request.session.get['user']}})
        user = userobj.json()
        courses = []
        for course in user:
            course_data = {'course-id':[course['course_id']]}
            cobj = requests.get(api_ip+'course/view', 
                    json=course_data, auth=udata)
            c = (cobj.json() if cobj.status_code == 200 else [])
            aobj = requests.get(api_ip+'assignment/view', 
                    json=course_data, auth=udata)
            c[0]['assignments'] = (aobj.json() if aobj.status_code == 200 else [])
            courses.append(c[0])
        return render_to_response('index.html', {'n':datetime.datetime.now(), 'user':user[0], 'courses':courses})
    else:
        return HttpResponseRedirect('/login')

def about(request):
	return render_to_response('about.html')


