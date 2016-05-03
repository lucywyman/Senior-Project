from django.http import *
from django.shortcuts import *
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from polymatheia.components.forms import *
from polymatheia.components.views.common import *
from datetime import datetime
import json, requests, urlparse

api_ip = settings.API_IP

def create_course(request):
    if not check_auth(request):
        return HttpResponseRedirect('/login')
    if request.method == 'POST':
        udata = (request.session.get('user'), request.session.get('pw'))
        obj = {}
        for i in request.POST:
            if i != 'csrfmiddlewaretoken':
                obj[i] = [request.POST[i]]
        c_obj = requests.post(api_ip+'course/add', json=obj,
                auth=udata, verify=False)
        if c_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Course', 'action':
                'created'})
        else:
            error = str(c_obj.status_code) + " error. Please try again."
    form = Course()
    return render(request, 'course/create_course.html', {'form':form})

def created_course(request):
    return render_to_response('course/created.html')

def course_list(request):
    if not check_auth(request):
        return HttpResponseRedirect('/login')
    udata = (request.session.get('user'), 
            request.session.get('pw'))
    user_courses = get_courses(request)
    upcoming = []
    courses = []
    for course in user_courses:
        course_data = {'course-id':[course['course_id']]}
        c_obj = requests.get(api_ip+'course/view', 
                json=course_data, auth=udata, verify=False)
        c = (c_obj.json() if c_obj.status_code == 200 else [])
        a_obj = requests.get(api_ip+'assignment/view', 
                json=course_data, auth=udata, verify=False)
        assign = (a_obj.json() if a_obj.status_code == 200 else [])
        c[0]['assignments'] = assign
        courses.append(c[0])
        for a in assign:
            end_time = datetime.strptime(a['end_date'], '%m/%d/%y %H:%M:%S')
            if end_time > datetime.now():
                upcoming.append(a)
            else:
                upcoming.append(a)
    return render_to_response('course/course-list.html', 
            {'user':user_courses[0], 'courses':courses, 'upcoming':upcoming})

def course(request):
    if not check_auth(request):
        return HttpResponseRedirect('/login')
    ## Super gross: we're guaranteed the url is /course/[0-9]+, so remove
    ## /course/ to get course number
    udata = (request.session.get('user'), 
            request.session.get('pw'))
    user = get_courses(request)
    upcoming, past = [], []
    course_num = request.path[8:]
    course_data = {'course-id':[course_num]}
    course_obj = requests.get(api_ip+'course/view', json=course_data,
            auth=udata, verify=False)
    course = (course_obj.json() if course_obj.status_code == 200 else [])
    a_obj = requests.get(api_ip+'assignment/view', json=course_data, auth=udata,
            verify=False)
    assign = (a_obj.json() if a_obj.status_code == 200 else [])
    for a in assign:
        end_time = datetime.strptime(a['end_date'], '%m/%d/%y %H:%M:%S')
        if end_time > datetime.now():
            upcoming.append(a)
        else:
            past.append(a)
    return render_to_response('course/course.html', 
            {'course':course[0], 'upcoming':upcoming, 'past':past, 'a':a_obj,
                'user':user[0]})

def edit_course(request):
    if not check_auth(request):
        return HttpResponseRedirect('/login')
    udata = (request.session.get('user'), 
            request.session.get('pw'))
    if request.method == 'POST':
        obj = {}
        for i in request.POST:
            if i != 'csrfmiddlewaretoken':
                obj[i] = [request.POST[i]]
        obj['course-id'] = request.path[13:] 
        c_obj = requests.post(api_ip + 'course/update', json=obj, 
                auth=udata, verify=False)
        if c_obj.status_code == 200:
            return render_to_response('edited.html', {'name':'Course',
                'aciont':'updated'})
        else:
            error = str(a_obj.status_code)+' error. Please try again'
    course_data = {'course-id':[course_id]}
    c_obj = requests.get(api_ip+'course/view', json=course_data, auth=udata, 
            verify=False)
    c = (c_obj.json() if c_obj.status_code == 200 else [])
    c = c[0]
    ## Format data for form population
    term = (b[0] for b in TERMS if c[term] in b)
    dept = (b[0] for b in DEPTS if c[dept] in b)
    form = Course(initial={'name':c['name'], 
        'num':c['course_num'],
        'term': term,
        'year':2016,
        'dept':dept})
    return render_to_response('course/edit_course.html', 
            {'form':form, 'course':c},
            context_instance=RequestContext(request))
