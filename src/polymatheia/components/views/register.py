from django.http import *
from django.shortcuts import *
from django.conf import settings
from django.template import RequestContext
from django.core.context_processors import csrf
from polymatheia.components.forms import *
from base64 import *
import requests

api_ip = settings.API_IP
CA_BUNDLE = settings.CA_BUNDLE

def register(request):
    if request.method == 'POST':
        if request.POST['password'] != request.POST['password2']:
            render_to_response('register/registration_form.html', 
                    {'form':form, 'error':'Your passwords did not match'})
        user_obj = requests.post(api_ip + 'student/add', json=request.POST, verify=CA_BUNDLE)
        return HttpResponseRedirect('/register/complete')
    form = User()
    return render_to_response('register/registration_form.html', {'form':form},
            RequestContext(request))

def registration_complete(request):
    return render_to_response('register/registration_complete.html')


