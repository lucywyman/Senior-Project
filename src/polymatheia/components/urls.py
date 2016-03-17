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
		url(r'^register/$', polymatheia.components.views.register, 
			name='register'),
		url(r'^register/complete/$', 
			polymatheia.components.views.registration_complete, 
			name='registration_complete')
		]
urlpatterns += staticfiles_urlpatterns()