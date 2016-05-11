from django.http import *
from django.shortcuts import *
from django.conf import settings
from django.template import RequestContext
from django.core.context_processors import csrf
from django.forms import formset_factory
from polymatheia.components.forms import *
from polymatheia.components.views.common import *
import json, requests, urlparse, re
from datetime import datetime

api_ip = settings.API_IP

def student_add(request):
    if not check_auth(request):
        return HttpResponseRedirect('/login')
    udata = (request.session.get('user'), request.session.get('pw'))
    pattern = re.compile("^student-([0-9])+$")
    if request.method == 'POST':
        obj = {'student':[], 'course-id':[request.POST['course-id']]}
        for i in request.POST:
            if (pattern.match(i) or i == 'student') and request.POST[i] != '':
                obj['student'].append(request.POST[i])
        raise Exception(obj)
        a_obj = requests.post(api_ip+'student/add', json=obj,
                auth=udata, verify=False)
        if a_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Students', 
                'action':'added'})
        else:
            error = str(a_obj.status_code) + " error. Please try again."
    r = [i for i in range(50)]
    students = requests.get(api_ip+'student/view', auth=udata, verify=False,
            json={})
    students = students.json()
    courses = get_courses(request)
    return render_to_response('students/add_student.html', {'range':r, 
        'students':students, 'courses':courses},RequestContext(request))

def student(request):
    if not check_auth(request):
        return HttpResponseRedirect('/login')
    udata = (request.session.get('user'), request.session.get('pw'))
    student_id = request.path[8:]
    student_data = {'student':[student_id]}
    user = get_courses(request)
    student_obj = requests.get(api_ip+'student/view', json=student_data, 
            auth=udata, verify=False)
    student = (student_obj.json() if student_obj.status_code == 200 else []) 
    return render_to_response('students/student.html', {'courses':student, 
        'user':user[0], 'student':student[0]})

def delete_student(request):
    udata = (request.session.get('user'), request.session.get('pw'))
    student_id = request.path[16:]
    student_data = {'student':[student_id]}
    if request.method == 'POST':
        s_obj = requests.delete(api_ip+'student/delete', json=student_data, 
                auth=udata, verify=False)
        if s_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Student', 
                'action':'deleted'})
        else:
            error = str(s_obj.status_code) + " error. Please try again"
    s_obj = requests.get(api_ip+'student/view', json=student_data, auth=udata,
            verify=False)
    s = (s_obj.json() if s_obj.status_code == 200 else [])
    u = get_courses(request)
    return render_to_response('students/delete_student.html',
            {'student':s[0], 'user':u[0]},
            context_instance=RequestContext(request))
