from django.http import HttpResponse

def index(request):
	return render_to_response('index.html')

def login(request):
	if request.REQUEST.get('username'):
		return(authenticate(request))
	return render_to_response('login.html', {}, 
			context_instance=RequestContext(request))
