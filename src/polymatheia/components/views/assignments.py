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

def create_assignment(request):
    udata = (request.session['user'], request.session['pw'])
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
                'action':'created', 'user':request.session['uinfo'], 
                'courses':request.session['courses']})
        else:
            error = str(a_obj.status_code) + " error. Please try again."
    form = Assignment()
    return render_to_response('assignment/create_assignment.html', 
            {'form':form, 'error':error, 'courses':request.session['courses'],
                'user':request.session['uinfo']}, RequestContext(request))

def assignment(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    courses = request.session['courses']
    assign_id = request.path[12:]
    assignment_data = {'assignment-id':[assign_id]}
    a_obj = requests.get(api_ip+'assignment/view', json=assignment_data,
            auth=udata, verify=CA_BUNDLE)
    assign = (a_obj.json() if a_obj.status_code == 200 else [])
    t_obj = requests.get(api_ip+'test/view', json=assignment_data,
            auth=udata, verify=CA_BUNDLE)
    t = (t_obj.json() if t_obj.status_code == 200 else [[]])
    if request.session.get('type') == 'student':
        assignment_data['student'] = [request.session['user']]
        s_obj = requests.get(api_ip+'submission/view', json=assignment_data,
                auth=udata, verify=CA_BUNDLE)
        s = (s_obj.json() if s_obj.status_code == 200 else [])
        if s != []:
            if s[0]['results']:
                results = json.loads(s[0]['results'])
                e = results['Errors']
                tap = results['TAP']
                g = results['Grade']
            return render_to_response('assignment/assignment.html', 
                    {'assignment':assign[0], 'user':courses[0], 'tests':t,
                        'sub':s[0], 'result':results, 'errors':e, 'tap':tap,
                        'courses':courses, 'grade':g},
                    RequestContext(request))
    return render_to_response('assignment/assignment.html',
            {'assignment':assign[0], 'user':courses[0], 'courses':courses}, 
            RequestContext(request))

def edit_assignment(request):
    if not check_auth:
        return HttpResponseRedirect('/login')
    udata = (request.session['user'], request.session['pw'])
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
                auth=udata, verify=CA_BUNDLE)
        if a_obj.status_code == 200:
            return render_to_response('assignment/updated.html')
        else:
            error = str(a_obj.status_code) + " error. Please try again."
    a_obj = requests.get(api_ip+'assignment/view', json=assignment_data, 
            auth=udata, verify=CA_BUNDLE)
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
            {'assignment':a,'form':form,'error':error,
                'courses':request.session['courses'],
                'user':request.session['uinfo']}, RequestContext(request))

def delete_assignment(request):
    udata = (request.session['user'], request.session['pw'])
    assignment_id = request.path[19:]
    assignment_data = {'assignment-id':[assignment_id]}
    if request.method == 'POST':
        c_obj = requests.delete(api_ip+'assignment/delete', json=assignment_data, 
                auth=udata, verify=CA_BUNDLE)
        if c_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Assignment', 
                'action':'deleted', 'user':request.session['uinfo'],
                'courses':request.session['courses']})
        else:
            error = str(r_obj.status_code) + " error. Please try again"
    c_obj = requests.get(api_ip+'assignment/view', json=assignment_data, auth=udata,
            verify=CA_BUNDLE)
    c = (c_obj.json() if c_obj.status_code == 200 else [])
    courses = request.session['courses']
    return render_to_response('assignment/delete_assignment.html',
            {'assignment':c[0], 'user':courses[0], 'courses':courses},
            context_instance=RequestContext(request))

def submit_assignment(request):
    udata = (request.session['user'], request.session['pw'])
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
                auth=udata, verify=CA_BUNDLE)
        if c_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Assignment', 
                'action':'submitted', 'user':request.session['courses']})
        else:
            error = str(c_obj.status_code) + " error. Please try again"
    assignment_data['student'] = request.session['user']
    c_obj = requests.get(api_ip+'submission/view', json=assignment_data, 
            auth=udata, verify=CA_BUNDLE)
    s = (c_obj.json() if c_obj.status_code == 200 else [])
    return render_to_response('submission/submission.html', {'sub':s,
        'user':request.session['uinfo'], 'courses':request.session['courses']})
