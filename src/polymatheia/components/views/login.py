from django.http import *
from django.shortcuts import *
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from polymatheia.components.forms import *

def login_user(request):
	#logout(request)
	username = password = ''
	## TODO How to log people in through API
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/index')
	return render_to_response('auth/login.html')


