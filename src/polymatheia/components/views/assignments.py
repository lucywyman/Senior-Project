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
                'action':'created'})
        else:
            error = str(a_obj.status_code) + " error. Please try again."
    courses = get_courses(request) 
    form = Assignment()
    return render_to_response('assignment/create_assignment.html', 
            {'form':form, 'error':error, 'courses':courses}, 
            RequestContext(request))

def assignment(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    if request.method == 'POST':
        a_obj = requests.post(api_ip+'assignment/submit', json=request.POST,
                auth=udata, verify=False)
        # TODO return test results here
    user = get_courses(request)
    assign_id = request.path[12:]
    assignment_data = {'assignment-id':[assign_id]}
    a_obj = requests.get(api_ip+'assignment/view', json=assignment_data,
            auth=udata, verify=False)
    assign = (a_obj.json() if a_obj.status_code == 200 else [])
    t_obj = requests.get(api_ip+'test/view', json=assignment_data,
            auth=udata, verify=False)
    if t_obj.status_code == 200:
        t = t_obj.json()
    else:
        t = [[]]
    form = Submission()
    return render_to_response('assignment/assignment.html', 
            {'assignment':assign[0], 'form':form, 'user':user[0], 
                'tests':t})

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
                'action':'deleted'})
        else:
            error = str(r_obj.status_code) + " error. Please try again"
    c_obj = requests.get(api_ip+'assignment/view', json=assignment_data, auth=udata,
            verify=False)
    c = (c_obj.json() if c_obj.status_code == 200 else [])
    u = get_courses(request)
    return render_to_response('assignment/delete_assignment.html',
            {'assignment':c[0], 'user':u[0]},
            context_instance=RequestContext(request))
