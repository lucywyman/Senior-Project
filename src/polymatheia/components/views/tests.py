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
        files = {"file": request.FILES['filepath'].read()}
        #raise Exception(files)
        #files = {"file": open(request.FILES['filepath'], 'rb')}
        t_obj = requests.post(api_ip+'test/add', data=obj, auth=udata, 
                files=files, verify=False)
        if t_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Test', 
                'action':'created'})
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
            assignments.append(a[0])
    form = Test()
    return render_to_response('test/create_test.html', 
            {'form':form, 'error':error, 'assignments':assignments}, 
            RequestContext(request))

def test(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    test_id = request.path[10:]
    if request.method == 'POST':
        # TODO Run tests and display results
        blee = 'blah'
    test_data = {'test-id':[test_id]}
    t_obj = requests.get(api_ip+'test/view', json=test_data,
            auth=udata, verify=False)
    test = (t_obj.json() if t_obj.status_code == 200 else [])
    form = Submission()
    return render_to_response('test/test.html', 
            {'test':assign, 'form':form})

def edit_test(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    test_id = request.path[10:]
    if request.method == 'POST':
        obj = {}
        for i in request.POST:
            if i != 'csrfmiddlewaretoken':
                obj[i] = [request.POST[i]]
        obj['test-id'] = test_id
        a_obj = requests.post(api_ip+'test/update', json=obj,
                auth=udata, verify=False)
        if a_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Test',
                'action':'updated'})
        else:
            error = str(a_obj.status_code) + " error. Please try again."
    test_data = {'test-id':[assign_id]}
    t_obj = requests.get(api_ip+'test/view', json=test_data, auth=udata,
            verify=False)
    a = t_obj.json()
    a = a[0]
    form = Test(initial={})
    return render_to_response('test/edit_test.html', 
            {'test':a,'form':form}, RequestContext(request))

def delete_test(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    if request.method == 'POST':
        return render_to_response('edited.html', {'name':'Test', 'action':
            'deleted'})
