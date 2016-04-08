from django.http import *
from django.shortcuts import *
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from polymatheia.components.forms import *
import json, requests, urlparse
from datetime import datetime

api_ip = settings.API_IP

def create_assignment(request):
    if request.method == 'POST':
        form = Course(request.POST)
        req = requests.post(api_ip + 'course/add')
        return HttpResponseRedirect('/assignment/created')
    else:
        form = Course()
    return render(request, 'assignment/create_assignment.html', {'form':form})

def assignment(request):
    if request.method == 'POST':
        form = Submission(request.POST)
        return HttpResponseRedirect('/assignment/submitted')
    assign_id = request.path[12:]
    assignment_data = {'assignment-id':[assign_id]}
    a_obj = requests.get(api_ip+'assignment/view', json=assignment_data)
    assign = a_obj.json()
    form = Submission()
    return render_to_response('assignment/assignment.html', 
            {'assignment':assign, 'form':form})

def edit_assignment(request):
    ## TODO
    if request.method == 'POST':
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
            {'assignment':a,'form':form})
