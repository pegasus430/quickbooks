from django.shortcuts import redirect

def index(request):
    response = redirect('/index/')
    return response