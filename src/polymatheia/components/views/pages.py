from django.shortcuts import render

def index(request):
    """
    Returns the index page for the site
    """
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')
