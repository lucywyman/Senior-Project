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

def create_test(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    error = ''
    if request.method == 'POST':
        obj = {}
        for i in request.POST:
            if i != 'csrfmiddlewaretoken':
                obj[i] = [request.POST[i]]
        files = {"file": request.FILES['tfile']}
        t_obj = requests.post(api_ip+'test/add', data=obj, auth=udata, 
                files=files, verify=False)
        if t_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Test', 
                'action':'created', 'user':request.session['courses']})
        else:
            error = t_obj.status_code + " error. Please try again."
    courses = get_courses(request)
    assignments = []
    for c in courses:
        course_data = {'course-id':[c['course_id']]}
        aobj = requests.get(api_ip+'assignment/view', 
                json=course_data, auth=udata, verify=False)
        if aobj.status_code == 200:
            a = aobj.json()
            assignments.extend(a)
    form = Test()
    return render_to_response('test/create_test.html', 
            {'form':form, 'error':error, 'assignments':assignments}, 
            RequestContext(request))

def test(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    test_id = request.path[6:]
    test_data = {'test-id':[test_id]}
    t_obj = requests.get(api_ip+'test/view', json=test_data,
            auth=udata, verify=False)
    test = (t_obj.json() if t_obj.status_code == 200 else [])
    u = get_courses(request)
    return render_to_response('test/test.html', {'test':test[0], 'user':u[0]})

def edit_test(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    test_id = request.path[11:]
    if request.method == 'POST':
        obj = {}
        for i in request.POST:
            if i != 'csrfmiddlewaretoken':
                obj[i] = [request.POST[i]]
        files = {"file": request.FILES['filepath'].read()}
        obj['test-id'] = test_id
        t_obj = requests.post(api_ip+'test/update', data=obj, auth=udata, 
                files=files, verify=False)
        if t_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Test', 
                'action':'created', 'user':request.session['courses']})
        else:
            error = t_obj.status_code + " error. Please try again."
    test_data = {'test-id':[test_id]}
    t_obj = requests.get(api_ip+'test/view', json=test_data, auth=udata,
            verify=False)
    t = t_obj.json()
    t = t[0]
    form = Test(initial={
        'name':t['test_name'],
        'points':t['points'],
        'time':t['time_limit']
        })
    return render_to_response('test/edit_test.html', 
            {'test':t,'form':form}, RequestContext(request))

def delete_test(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    test_id = request.path[15:]
    test_data = {'test-id':[test_id]}
    if request.method == 'POST':
        c_obj = requests.delete(api_ip+'test/delete', json=test_data, 
                auth=udata, verify=False)
        if c_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Test', 
                'action':'deleted', 'user':request.session['courses']})
        else:
            error = str(r_obj.status_code) + " error. Please try again"
    c_obj = requests.get(api_ip+'test/view', json=test_data, auth=udata,
            verify=False)
    c = (c_obj.json() if c_obj.status_code == 200 else [])
    u = get_courses(request)
    return render_to_response('test/delete_test.html',
            {'test':c[0], 'user':u[0]},
            context_instance=RequestContext(request))
