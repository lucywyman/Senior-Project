from django.http import *
from django.shortcuts import *
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from polymatheia.components.forms import *
from polymatheia.components.views import get_courses
import requests, json

api_ip = settings.API_IP

def login_user(request):
    if request.method == 'POST':
        request.session['user'] = request.POST['username']
        request.session['pw'] = request.POST['password']
        udata = (request.POST['username'], request.POST['password'])
        headers = {'content-type':'application/json'}
        login = requests.post(api_ip+'login/as/', auth=udata, verify=False,
                headers=headers, json={})
        if login.status_code == 200:
            l_obj = login.json()
            request.session['type'] = l_obj['auth_level']
            request.session['courses'] = get_courses(request)
            return HttpResponseRedirect('/')
        else:
            render_to_response('auth/login.html', 
                    {'error':"Invalid username or password"},
                    RequestContext(request))
    return render_to_response('auth/login.html', RequestContext(request))

def logout_user(request):
    request.session.flush()
    return render_to_response('auth/logout.html')
