from django.http import *
from django.shortcuts import *
from django.template import RequestContext
from django.core.context_processors import csrf
from polymatheia.components.forms import *

def create_course(request):
	if request.method == 'POST':
		form = Course(request.POST)
		## This is where we send data to the API
		## If it returns good, redirect to success page, otherwise to error
		return HttpResponseRedirect('/course/created')
	else:
		form = Course()
	return render(request, 'course/create_course.html', {'form':form})
