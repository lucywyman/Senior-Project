from django.conf.urls import patterns, include, url 
from django.conf import settings

urlpatterns = patterns(
        '', 
        (r'^', include('polymatheia.components.urls')),
        ) 
