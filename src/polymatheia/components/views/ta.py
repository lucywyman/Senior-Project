from django.http import *
from django.shortcuts import *
from django.conf import settings
from django.template import RequestContext
from django.core.context_processors import csrf
from polymatheia.components.forms import *
from polymatheia.components.views.common import *
import json, requests, urlparse
from datetime import datetime

api_ip = settings.API_IP

def create_ta(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    error = ''
    if request.method == 'POST':
        obj = {}
        for i in request.POST:
            if i != 'csrfmiddlewaretoken':
                obj[i] = [request.POST[i]]
        t_obj = requests.post(api_ip+'ta/add', json=obj, auth=udata, 
                verify=False)
        if t_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'TA', 'action':
                'created'})
        else:
            error = t_obj.status_code + " error. Please try again."
    form = TA()
    courses = get_courses(request)
    return render_to_response('ta/create_ta.html', 
            {'form':form, 'error':error, 'courses':courses}, 
            RequestContext(request))

def edit_ta(request):
    pass

def ta(request):
    pass

def delete_ta(request):
    pass
