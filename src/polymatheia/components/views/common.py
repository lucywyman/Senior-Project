from django.conf import settings
import requests, json

api_ip = settings.API_IP
CA_BUNDLE = settings.CA_BUNDLE

def check_auth(request):
    '''
    Check if a user is logged in and has a session
    '''
    if request.session.get('user'):
        return True
    else:
        return False

def get_courses(request):
    '''
    Returns a list of courses that a user is enrolled in or teacher
    '''
    udata = (request.session.get('user'), 
            request.session.get('pw'))
    if request.session['type'] == 'student':
        user_info = {'student':[request.session['user']]}
        user_obj = requests.get(api_ip+'student/view', 
                json=user_info, auth=udata, verify=CA_BUNDLE)
        if user_obj.status_code != 204:
            courses = user_obj.json()
        else:
            courses = []
    elif request.session['type'] == 'ta':
        user_info = {'ta-id':[request.session['user']]}
        user_obj = requests.get(api_ip+'ta/view',
            json=user_info, auth=udata, verify=CA_BUNDLE)
        courses = user_obj.json()
    else:
        user_info = {'teacher':[request.session['user']]}
        user_obj = requests.get(api_ip+'course/view',
                json=user_info, auth=udata, verify=CA_BUNDLE)
        courses = user_obj.json()
    return courses
