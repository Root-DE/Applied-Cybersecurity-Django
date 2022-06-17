from django.shortcuts import render
from requests import request
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import sys

# Create your views here.

def auth_login(request):
    if request.method == 'POST':
        print("POST")
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print("user: ", user)
        if user is not None:
            print("user is not None")
            return dashboard(request)
        else:
            print("user is None")
            return auth_login(request)
    if request.user.is_authenticated:
        print("user is authenticated")
        return dashboard(request)
    else:
        print("user is not authenticated")
        return render(request, 'auth_login.html')

# def auth_logout(request):
#     if request.user is not None:
#         logout(request)
#         return render(request, 'auth_login.html')

@login_required
def dashboard(request):
    print("dashboard", file=sys.stderr)
    print(request.user.username, file=sys.stderr)
    return render(request, 'dashboard.html', {"name": request.user.username})

@login_required
def dashboard2(request):
    print("dashboard2", file=sys.stderr)
    print(request.user.username, file=sys.stderr)
    return render(request, 'dashboard2.html', {"name": request.user.username})
