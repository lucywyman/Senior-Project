from django.shortcuts import render

def index(request):
    """
    */
    Returns the index page for the site
    """
    return render(request, 'index.html')

def about(request):
    """
    */about.html
    Returns the about page for this project
    """
    return render(request, 'about.html')
