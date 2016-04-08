from django.http import *
from django.shortcuts import *
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from polymatheia.components.forms import *
from datetime import datetime
import json, requests, urlparse

api_ip = settings.API_IP

def create_course(request):
    if request.method == 'POST':
        form = Course(request.POST)
        req = requests.post(api_ip + 'course/add')
        return HttpResponseRedirect('/course/created')
    else:
        form = Course()
    return render(request, 'course/create_course.html', {'form':form})

def course_list(request):
    user_data = {'student':['hennign']}
    user_obj = requests.get(api_ip+'student/view', json=user_data)
    user = user_obj.json()
    upcoming = []
    courses = []
    for course in user:
        course_data = {'course-id':[course['course_id']]}
        c_obj = requests.get(api_ip+'course/view', json=course_data)
        c = c_obj.json()
        a_obj = requests.get(api_ip+'assignment/view', json=course_data)
        assign = a_obj.json()
        c[0]['assignments'] = assign
        courses.append(c[0])
        for a in assign:
            end_time = datetime.strptime(a['end_date'], '%m/%d/%y %H:%M:%S')
            if end_time > datetime.now():
                upcoming.append(a)
            else:
                upcoming.append(a)
    return render_to_response('course/course-list.html', 
            {'user':user[0], 'courses':courses, 'upcoming':upcoming})

def course(request):
    ## Super gross: we're guaranteed the url is /course/[0-9]+, so remove
    ## /course/ to get course number
    upcoming, past = [], []
    course_num = request.path[8:]
    course_data = {'course-id':[course_num]}
    course_obj = requests.get(api_ip+'course/view', json=course_data)
    course = course_obj.json()
    a_obj = requests.get(api_ip+'assignment/view')
    assign = a_obj.json()
    for a in assign:
        end_time = datetime.strptime(a['end_date'], '%m/%d/%y %H:%M:%S')
        if end_time > datetime.now():
            upcoming.append(a)
        else:
            past.append(a)
    return render_to_response('course/course.html', 
            {'course':course, 'upcoming':upcoming, 'past':past, 'a':a_obj})

def edit_course(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/course/edited')
    course_id = request.path[13:] 
    course_data = {'course-id':[course_id]}
    c_obj = requests.get(api_ip+'course/view', json=course_data)
    c = c_obj.json()
    c = c[0]
    ## Format data for form population
    term = (b[0] for b in TERMS if c[term] in b)
    form = Assignment(initial={'name':c['name'], 
        'course_num':c['name'],
        'term': term,
        'year':2016,
        'dept':DEPTS})
    return render_to_response('course/edit_course.html', 
            {'form':form, 'course':c})
