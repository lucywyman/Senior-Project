from django.http import *
from django.shortcuts import *
from django.conf import settings
from django.template import RequestContext
from django.core.context_processors import csrf
from polymatheia.components.forms import *
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
                if i == 'course_id':
                    obj['course-id'] = [request.POST[i]]
                else:
                    obj[i] = [request.POST[i]]
        a_obj = requests.post(api_ip+'assignment/add', json=obj,
                auth=udata)
        if a_obj.status_code == 200:
            return render_to_response('assignment/created.html')
        else:
            error = a_obj.status_code + " error. Please try again."
    form = Assignment()
    return render_to_response('assignment/create_assignment.html', 
            {'form':form, 'error':error}, RequestContext(request))

def created_assignment(request):
    return render_to_response('assignment/created.html')

def assignment(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    if request.method == 'POST':
        a_obj = requests.post(api_ip+'assignment/submit', json=request.POST,
                auth=udata)
        return HttpResponseRedirect('/assignment/submitted')
    assign_id = request.path[12:]
    assignment_data = {'assignment-id':[assign_id]}
    a_obj = requests.get(api_ip+'assignment/view', json=assignment_data,
            auth=udata)
    assign = (a_obj.json() if a_obj.status_code == 200 else [])
    form = Submission()
    return render_to_response('assignment/assignment.html', 
            {'assignment':assign, 'form':form})

def edit_assignment(request):
    if request.method == 'POST':
        a_obj = requests.post(api_ip + 'assignment/add', json=request.POST)
        return HttpResponseRedirect('/assignment/edited')
    assign_id = request.path[17:] 
    assignment_data = {'assignment-id':[assign_id]}
    a_obj = requests.get(api_ip+'assignment/view', json=assignment_data)
    a = a_obj.json()
    a = a[0]
    ## Format data for form population
    begin_time = datetime.strptime(a['begin_date'], '%m/%d/%y %H:%M:%S')
    end_time = datetime.strptime(a['end_date'], '%m/%d/%y %H:%M:%S')
    level = FEEDBACK[a['feedback_level']-1][1]
    form = Assignment(initial={'name':a['name'], 
        #'begin_date':begin_time,
        #'end_date':end_time,
        #'submission_limit':a['submission_limit'],
            'feedback_level':level})
    return render_to_response('assignment/edit_assignment.html', 
            {'assignment':a,'form':form}, RequestContext(request))
