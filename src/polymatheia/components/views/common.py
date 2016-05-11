from django.conf import settings
import requests, json

api_ip = settings.API_IP

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
                json=user_info, auth=udata, verify=False)
        courses = user_obj.json()
    elif request.session['type'] == 'ta':
        #user_info = {'ta-id':[request.session['user']]}
        #user_obj = requests.get(api_ip+'course/view',
        #    json=user_info, auth=udata, verify=False)
        courses = [[]]
    else:
        user_info = {'teacher':[request.session['user']]}
        user_obj = requests.get(api_ip+'course/view',
                json=user_info, auth=udata, verify=False)
        courses = user_obj.json()
    return courses
