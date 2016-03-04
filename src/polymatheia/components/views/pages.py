from django.http import *
from django.shortcuts import *
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from polymatheia.components.forms import *

def index(request):
	return render_to_response('index.html')

def about(request):
	return render_to_response('about.html')


