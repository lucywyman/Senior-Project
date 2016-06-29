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
CA_BUNDLE = settings.CA_BUNDLE

def create_ta(request):
    if not check_auth(request):
        return HttpResponseRedirect('/login')
    udata = (request.session['user'], request.session['pw'])
    error = ''
    if request.method == 'POST':
        obj = {}
        for i in request.POST:
            if i != 'csrfmiddlewaretoken':
                obj[i] = [request.POST[i]]
        t_obj = requests.post(api_ip+'ta/add', json=obj, auth=udata, 
                verify=CA_BUNDLE)
        if t_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'TA', 'action':
                'added', 'user':request.session['uinfo'],
                'courses':request.session['courses']})
        else:
            error = t_obj.status_code + " error. Please try again."
    courses = get_courses(request)
    ta_obj = requests.get(api_ip+'ta/view', json={}, auth=udata, verify=CA_BUNDLE)
    tas = ta_obj.json()
    uniq = []
    for ta in tas:
        if ta['ta_id'] in uniq:
            tas.remove(ta)
        else:
            uniq.append(ta['ta_id'])
    return render_to_response('ta/create_ta.html', 
            {'error':error, 'courses':courses, 'tas':tas}, 
            RequestContext(request))

def ta(request):
    if not check_auth(request):
        return HttpResponseRedirect('/login')
    udata = (request.session.get('user'), request.session.get('pw'))
    ta_id = request.path[4:]
    ta_data = {'ta':[ta_id]}
    ta_obj = requests.get(api_ip+'ta/view', json=ta_data, auth=udata,
            verify=CA_BUNDLE)
    ta = (ta_obj.json() if ta_obj.status_code == 200 else []) 
    courses = request.session['courses']
    return render_to_response('ta/ta.html', {'ta':ta, 'user':courses[0], 
        'name':ta['ta'], 'courses':courses})

def delete_ta(request):
    pass
