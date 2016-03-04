from django.http import *
from django.shortcuts import *
from django.template import RequestContext
from django.core.context_processors import csrf
from polymatheia.components.forms import *

def register(request):
	if request.method == 'POST':
		form = NewUser(request.POST)
		if form.is_valid():
			return HttpResponseRedirect('/register/complete')
	else:
		form = NewUser()
	token = {}
	token.update(csrf(request))
	token['form'] = form
	return render(request, 'register/registration_form.html', {'form':form})

def registration_complete(request):
	return render_to_response('register/registration_complete.html')


