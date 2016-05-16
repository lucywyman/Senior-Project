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

def create_assignment(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    error = ''
    if request.method == 'POST':
        obj = {}
        for i in request.POST:
            if i != 'csrfmiddlewaretoken':
                obj[i] = [request.POST[i]]
        a_obj = requests.post(api_ip+'assignment/add', json=obj,
                auth=udata, verify=False)
        if a_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Assignment', 
                'action':'created', 'user':request.session['courses']})
        else:
            error = str(a_obj.status_code) + " error. Please try again."
    courses = get_courses(request) 
    form = Assignment()
    return render_to_response('assignment/create_assignment.html', 
            {'form':form, 'error':error, 'courses':courses}, 
            RequestContext(request))

def assignment(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    user = get_courses(request)
    assign_id = request.path[12:]
    assignment_data = {'assignment-id':[assign_id]}
    a_obj = requests.get(api_ip+'assignment/view', json=assignment_data,
            auth=udata, verify=False)
    assign = (a_obj.json() if a_obj.status_code == 200 else [])
    t_obj = requests.get(api_ip+'test/view', json=assignment_data,
            auth=udata, verify=False)
    t = (t_obj.json() if t_obj.status_code == 200 else [[]])
    if request.session.get('type') == 'student':
        assignment_data['student'] = [request.session.get('user')]
        s_obj = requests.get(api_ip+'submission/view', json=assignment_data,
                auth=udata, verify=False)
        s = (s_obj.json() if s_obj.status_code == 200 else [])
    else:
        s = []
    return render_to_response('assignment/assignment.html', 
            {'assignment':assign[0], 'user':user[0], 'tests':t, 'subs':s}, 
            RequestContext(request))

def edit_assignment(request):
    if not check_auth:
        return HttpResponseRedirect('/login')
    udata = (request.session.get('user'), request.session.get('pw'))
    error = ''
    assign_id = request.path[17:] 
    assignment_data = {'assignment-id':[assign_id]}
    if request.method == 'POST':
        obj = {}
        for i in request.POST:
            if i != 'csrfmiddlewaretoken':
                obj[i] = [request.POST[i]]
        obj['assignment-id'] = assign_id
        a_obj = requests.post(api_ip+'assignment/update', json=obj,
                auth=udata, verify=False)
        if a_obj.status_code == 200:
            return render_to_response('assignment/updated.html')
        else:
            error = str(a_obj.status_code) + " error. Please try again."
    courses = get_courses(request)
    a_obj = requests.get(api_ip+'assignment/view', json=assignment_data, 
            auth=udata, verify=False)
    a = a_obj.json()
    a = a[0]
    ## Format data for form population
    begin_time = datetime.strptime(a['begin_date'], '%m/%d/%y %H:%M:%S')
    end_time = datetime.strptime(a['end_date'], '%m/%d/%y %H:%M:%S')
    level = FEEDBACK[a['feedback_level']-1][1]
    form = Assignment(initial={'name':a['name'], 
            'begin_date':begin_time,
            'end_date':end_time,
            'submission_limit':a['submission_limit'],
            'feedback_level':level})
    return render_to_response('assignment/edit_assignment.html', 
            {'assignment':a,'form':form,'error':error,'courses':courses}, 
            RequestContext(request))

def delete_assignment(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    assignment_id = request.path[19:]
    assignment_data = {'assignment-id':[assignment_id]}
    if request.method == 'POST':
        c_obj = requests.delete(api_ip+'assignment/delete', json=assignment_data, 
                auth=udata, verify=False)
        if c_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Assignment', 
                'action':'deleted', 'user':request.session['courses']})
        else:
            error = str(r_obj.status_code) + " error. Please try again"
    c_obj = requests.get(api_ip+'assignment/view', json=assignment_data, auth=udata,
            verify=False)
    c = (c_obj.json() if c_obj.status_code == 200 else [])
    u = get_courses(request)
    return render_to_response('assignment/delete_assignment.html',
            {'assignment':c[0], 'user':u[0]},
            context_instance=RequestContext(request))

def submit_assignment(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    assignment_id = request.path[19:]
    assignment_data = {'assignment-id':[assignment_id]}
    if request.method == 'POST':
        obj = {'assignment-id': [assignment_id]}
        files = {}
        i = 0
        for f in request.FILES.getlist('files'):
            files['file'+str(i)] = f
            i = i+1
        c_obj = requests.post(api_ip+'submission/add', data=obj, files=files,
                auth=udata, verify=False)
        if c_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Assignment', 
                'action':'submitted', 'user':request.session['courses']})
        else:
            error = str(r_obj.status_code) + " error. Please try again"
    assignment_data['student'] = request.session.get('user')
    c_obj = requests.get(api_ip+'submission/view', json=assignment_data, 
            auth=udata, verify=False)
    s = (c_obj.json() if c_obj.status_code == 200 else [])
    u = get_courses(request)
    return render_to_response('submission/submission.html', {'sub':s,
        'user':u[0]})
