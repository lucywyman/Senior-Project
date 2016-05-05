"""polymatheia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import polymatheia.components.views
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

'''
Since we import all views into __init__.py in the views dir,
we can directly call those functions instead of the files they are 
embedded in.
'''
urlpatterns = [
        url(r'^$', polymatheia.components.views.index, name='index'),
        url(r'^about$', polymatheia.components.views.about, name='about'),
        url(r'^login/$', polymatheia.components.views.login_user, 
            name='login'),
        url(r'^logout/$', polymatheia.components.views.logout_user,
            name='logout'),
        url(r'^register/$', polymatheia.components.views.register, 
            name='register'),
        url(r'^register/complete/$', 
            polymatheia.components.views.registration_complete, 
            name='registration_complete'),
        url(r'^courses/$', polymatheia.components.views.course_list,
            name='courses'),
        url(r'^course/[0-9]+$', polymatheia.components.views.course,
            name='course-details'),
        url(r'^course/create', polymatheia.components.views.create_course,
            name='create-course'),
        url(r'^course/edit/[0-9]+$', polymatheia.components.views.edit_course,
            name='edit-course'),
        url(r'^course/delete/[0-9]+$', polymatheia.components.views.delete_course,
            name='delete-course'),
        url(r'^assignment/[0-9]+$', polymatheia.components.views.assignment,
            name='assignment-details'),
        url(r'^assignment/create', 
            polymatheia.components.views.create_assignment,
            name='assignment-create'),
        url(r'^assignment/edit/[0-9]+$', 
            polymatheia.components.views.edit_assignment,
            name='edit-assignment'),
        url(r'^assignment/delete/[0-9]+$',
            polymatheia.components.views.delete_assignment,
            name='delete-assignment'),
        url(r'^test/[0-9]+$', polymatheia.components.views.test,
            name='test-details'),
        url(r'^test/create', 
            polymatheia.components.views.create_test,
            name='test-create'),
        url(r'^test/edit/[0-9]+$', 
            polymatheia.components.views.edit_test,
            name='edit-test'),
        url(r'^test/delete/[0-9]+$',
            polymatheia.components.views.delete_test,
            name='delete-test'),
        url(r'^ta/[0-9]+$', polymatheia.components.views.ta,
            name='ta-details'),
        url(r'^ta/create', 
            polymatheia.components.views.create_ta,
            name='ta-create'),
        url(r'^ta/edit/[0-9]+$', 
            polymatheia.components.views.edit_ta,
            name='edit-ta'),
        url(r'^ta/delete/[0-9]+$',
            polymatheia.components.views.delete_ta,
            name='ta-delete'),
        ]
urlpatterns += staticfiles_urlpatterns()
