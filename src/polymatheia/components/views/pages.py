from django.http import *
from django.shortcuts import *
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from polymatheia.components.forms import *
import datetime, json, requests

def index(request):
    data = {'required':''}
    user = requests.post(settings.API_IP+'student/view', json=data)
    course = requests.post(settings.API_IP+'course/view', json=data)
    return render_to_response('index.html', {'n':datetime.datetime.now(), 'user':user, 'course':course})

def about(request):
	return render_to_response('about.html')


