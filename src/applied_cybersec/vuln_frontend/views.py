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
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            return render(request, 'dashboard.html')
        else:
            return render(request, 'auth_login.html')
    if request.user.is_authenticated:
        return render(request, 'dashboard.html')
    else:
        return render(request, 'auth_login.html')

# def auth_logout(request):
#     if request.user is not None:
#         logout(request)
#         return render(request, 'auth_login.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')