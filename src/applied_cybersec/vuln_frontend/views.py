from unicodedata import name
from django.shortcuts import render
from requests import request
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import JsonResponse
import sys

from vuln_backend.models import *

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
    # ------------------------------------
    # get all the data we want to display
    # ------------------------------------
    # get some global statistics
    # TODO

    # get the newest statistics for each repository
    repositories = Repositories.objects.all().order_by('name')
    print("length", len(repositories), file=sys.stderr)
    scan_data = []
    for repository in repositories:
        latest_scan = ScanData.objects.filter(repository=repository).latest('created_at')
        statistics = Statistics.objects.filter(scan=latest_scan)[0]
        scan_data.append({
            'repo_name': repository.name,
            'repo_id': repository.id,
            'scan_date': str(latest_scan.created_at),
            # 'statistics': statistics,
            'number_vuln_critical': statistics.number_vuln_critical,
            'number_vuln_high': statistics.number_vuln_high,
            'number_vuln_medium': statistics.number_vuln_medium,
            'number_vuln_low': statistics.number_vuln_low,
            'number_vuln_negligible': statistics.number_vuln_negligible, 
        })

    print(scan_data)

    return render(request, 'dashboard.html', {"name": request.user.username, 'scan_data': scan_data}) 

@login_required
def dashboard2(request):
    print("dashboard2", file=sys.stderr)
    print(request.user.username, file=sys.stderr)
    return render(request, 'dashboard2.html', {"name": request.user.username})

def error_500(request):
    return render(request, '500.html')

@login_required
def download(type, repoid, created_at):
    filename = type + "_" + str(repoid) + "_" + str(created_at)
    scan_data = ScanData.objects.get(created_at=created_at, repository=repoid)
    sbom_json = scan_data.syft_scan
    response = JsonResponse(sbom_json)
    # as download
    response['Content-Disposition'] = 'attachment; filename="' + filename + '.json"'
    return response