from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.paginator import Paginator
import pytz

from vuln_backend.models import *

# Create your views here.

@login_required(login_url='/')
@csrf_exempt
def dashboard(request):
    # ====================================
    # check if it is an ajax request
    # ====================================
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # ------------------------------------
    # get all the data we want to display
    # ------------------------------------
    # get some global statistics
    # TODO

    # get the newest statistics for each repository
    repositories = Repositories.objects.all().order_by('name')

    # get all organizations
    organizations = set(repositories.values_list('organization', flat=True))

    # if we have an ajax request, we have have to filter the repositories
    search_term = None
    search_org = None
    vuln_search = False
    if is_ajax:
        if 'POST' == request.method:
            # try to get the search term from the request
            search_term = request.POST.get('search_term', '')
            search_org = request.POST.get('search_org', '')
            # do we have a cve search?
            if search_term:
                if 'cve' in search_term.lower():
                    vuln_search = True
                else:
                    repositories = repositories.filter(name__icontains=search_term)
            
            if search_org and search_org != 'all':
                print(search_org)
                repositories = repositories.filter(organization=search_org)

    # searched scans
    searched_scan_ids = []
    if vuln_search:
        searched_vulns = Vulnerabilities.objects.filter(vuln_id__icontains=search_term)
        for vuln in searched_vulns:
            searched_scan_ids += vuln.scan.all().values_list('id', flat=True)

    # get the latest scan for each repository
    latest_scans = []
    for repository in repositories:
        # get the latest scan
        scan = ScanData.objects.filter(repository=repository).latest('created_at')
        # if vulns are searched, check if this scan contains the searched vulns
        if vuln_search and scan.id not in searched_scan_ids:
            continue
        # add the scan to the list
        latest_scans.append(scan)

    scan_data = []
    for latest_scan in latest_scans:
        statistics = Statistics.objects.filter(scan=latest_scan).values().first()
        scan_data.append({
            'repo_org': latest_scan.repository.organization,
            'repo_name': latest_scan.repository.name,
            'repo_id': latest_scan.repository.id,
            'scan_date': str(latest_scan.created_at),
            'workflow_id': latest_scan.workflow_id,
            'statistics': statistics
        })

    if not is_ajax:
        return render(request, 'dashboard.html', {"name": request.user.username, 'scan_data': scan_data, 'organizations': organizations})
    
    ajax_data = {
        'card_deck': render_to_string('./dashboard_page/card_deck.html', {'scan_data': scan_data}),
        'graph_data': scan_data
    }
    return JsonResponse(ajax_data) 

def error_500(request):
    return render(request, '500.html')

@login_required(login_url='/')
def download(request):
    # get workflow_id from request
    workflow_id = request.POST.get('workflow_id')
    result_type = request.POST.get('result_type')

    filename = result_type + "_" + str(workflow_id)
    scan_data = ScanData.objects.get(workflow_id=workflow_id)
    
    if result_type == "sbom":
        output = scan_data.syft_scan
    if result_type == "vuln":
        output = scan_data.grype_scan
    response = JsonResponse(output)
    # as download
    response['Content-Disposition'] = 'attachment; filename="' + filename + '.json"'
    return response

@login_required(login_url='/')
@csrf_exempt
def details(request, repo_org, repo_name):
    # ====================================
    # check if it is an ajax request
    # ====================================
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # ====================================
    # get all data we need
    # ====================================
    # get the repo
    repo = Repositories.objects.get(organization=repo_org, name=repo_name)
    if repo is None:
        return render(request, '404.html')

    # get all scans for this repo
    scans = ScanData.objects.filter(repository_id=repo).order_by('created_at')

    # get all statistics for the scans and order by created_at
    statistics = Statistics.objects.filter(scan_id__in=scans).order_by('scan__created_at')


    # ====================================
    # extract all get parameters
    # ====================================
    # get the selected date
    actual_date = None
    if request.GET.get('date'):
        actual_date = datetime.strptime(request.GET.get('date'), '%d-%m-%Y %H:%M:%S')


    # get the scan of the selected date
    selected_scan = {}
    if actual_date is not None:
        try:
            selected_scan['scan'] = scans.filter(created_at__lte=actual_date).values('id', 'created_at', 'workflow_id', 'repository_id').latest('created_at')
        except ScanData.DoesNotExist:
            # get the first scan because the date is too old
            selected_scan['scan'] = scans.values('id', 'created_at', 'workflow_id', 'repository_id').latest('-created_at')
    else:
        # get the newest scan because no date is selected
        selected_scan['scan'] = scans.values('id', 'created_at', 'workflow_id', 'repository_id').latest('created_at')
    actual_date = selected_scan['scan']['created_at']

    selected_scan['scan']['date'] = actual_date.date().strftime('%d-%m-%Y')
    selected_scan['scan']['time'] = actual_date.time().strftime('%H:%M:%S')
    selected_scan['scan']['created_at'] = selected_scan['scan']['created_at']

    # get the statistics of the selected scan
    selected_scan['statistics'] = statistics.filter(scan=selected_scan['scan']['id']).values().first()



    # ====================================
    # Extract all vulnerability data + additional information like artifacts
    # ====================================
    # get the vulnerabilities for the selected scan
    vulnerabilities = Vulnerabilities.objects.filter(scan=selected_scan['scan']['id']).order_by('-vuln_id')

    # check if we have an ajax search
    page = 1
    search_term = None
    sort_vulns = False
    if is_ajax:
        if request.method == 'POST':
            # get the page of the infinite scroll
            page = int(request.POST.get('page')) if 'page' in request.POST else 1       
            # get the search term
            search_term = request.POST.get('search_term').strip() if 'search_term' in request.POST else None
            # get filter method
            if 'action' in request.POST and request.POST.get('action') in ['filter', 'infinit_scroll']:
                sort_vulns = True

    # if there is a search term, filter the vulnerabilities
    if search_term != "" and search_term is not None:
        # get the vulnerabilities
        vulnerabilities = vulnerabilities.filter(vuln_id__icontains=search_term)

    if sort_vulns:
        if request.POST.get('filter_type') == 'vuln_id':
            # order vulns based on id order (alphabetically)
            if request.POST.get('filter_direction') == 'asc':
                vulnerabilities = sorted(vulnerabilities, key=lambda x: x.vuln_id, reverse=True)
            else:
                vulnerabilities = sorted(vulnerabilities, key=lambda x: x.vuln_id)
        if request.POST.get('filter_type') == 'severity':
            # order vulns based on severity order
            severity_order = ['Critical', 'High', 'Medium', 'Low', 'Negligible', 'Unknown']
            if request.POST.get('filter_direction') == 'asc':
                vulnerabilities = sorted(vulnerabilities, key=lambda x: severity_order.index(x.severity))
            else:
                vulnerabilities = sorted(vulnerabilities, key=lambda x: severity_order.index(x.severity), reverse=True)
        if request.POST.get('filter_type') == 'status':
            # order vulns based on fix status order
            status_order = ['fixed','unknown','not-fixed','wont-fix']
            if request.POST.get('filter_direction') == 'asc':
                vulnerabilities = sorted(vulnerabilities, key=lambda x: status_order.index(x.fix['state']))
            else:
                vulnerabilities = sorted(vulnerabilities, key=lambda x: status_order.index(x.fix['state']), reverse=True)
        if request.POST.get('filter_type') == 'cvss':
            # order vulns based on id order (alphabetically)
            if request.POST.get('filter_direction') == 'asc':
                vulnerabilities = sorted(vulnerabilities, key=lambda x: x.cvss[0]['metrics']['baseScore'] if len(x.cvss) > 0 else 0, reverse=True)
            else:
                vulnerabilities = sorted(vulnerabilities, key=lambda x: x.cvss[0]['metrics']['baseScore'] if len(x.cvss) > 0 else 0)

    # parse the vulnerabilities to a list of dicts with additional artifact information
    vuln_list = []
    # we have to get the vulnerable artifact data!
    for vulnerability in vulnerabilities:
        vuln_obj = {}
        vuln_obj['vulnerability'] = vulnerability
        # 1. get all artifacts for this vulnerability
        artifacts_vuln = vulnerability.artifact.all()
        # 2. get the right artifact(s), that belong to the selected scan
        artifacts_vuln = artifacts_vuln.filter(scan=selected_scan['scan']['id'])
        # extract the cpe information
        for artifact in artifacts_vuln:
            vuln_obj['cpes'] = artifact.cpes
        
        vuln_list.append(vuln_obj)

    # apply pagination
    paginator = Paginator(vuln_list, 40)
    # adjust the elided pages
    vuln_page_obj = paginator.get_page(page)

    # ====================================
    # get other scans that were done on the same day
    # ====================================
    scans = scans.values('id', 'created_at', 'workflow_id', 'repository_id')

    # collect all scans from the selected date
    selected_scan['other_scans'] = [selected_scan['scan']['time']]
    date = actual_date.date()
    for scan in scans:
        if scan["created_at"].date() == date and scan["id"] != selected_scan['scan']['id']:
            selected_scan['other_scans'].append(scan["created_at"].time().strftime('%H:%M:%S'))#.astimezone(berlin)
    # sort the others scans by time descending
    selected_scan['other_scans'].sort(reverse=True)


    # create dict for the graph visualization
    graph_data = {
        'created_at': [],
        'unknown': [],
        'negligible': [],
        'low': [],
        'medium': [],
        'high': [],
        'critical': [],
    }

    statistics = statistics.values()

    for scan in scans:
        # format date to epoch time
        graph_data["created_at"].append(scan["created_at"].strftime("%Y-%m-%d %H:%M:%S"))

    for stat in statistics:
        graph_data["unknown"].append(stat["number_vuln_unknown"])
        graph_data["negligible"].append(stat["number_vuln_negligible"])
        graph_data["low"].append(stat["number_vuln_low"])
        graph_data["medium"].append(stat["number_vuln_medium"])
        graph_data["high"].append(stat["number_vuln_high"])
        graph_data["critical"].append(stat["number_vuln_critical"])

    # create the context
    context = {
        'repo': repo,
        'scans': scans,
        'statistics': statistics,
        'selected_scan': selected_scan,
        'paginator': paginator,
        'vuln_page_obj': vuln_page_obj,
        'graph_data': graph_data,
        'end_pagination': True if page >= paginator.num_pages else False,
    }
    if not is_ajax:
        return render(request, './details_page/details.html', context)

    # check if a new scan is selected or pagination is used
    ajax_data = {}
    if request.method == 'POST' and 'action' in request.POST:
        if request.POST['action'] == 'select_scan':
            ajax_data = {
                'vuln_table': render_to_string('./details_page/vuln_table.html', {'vuln_page_obj': vuln_page_obj}),
                'scan_data': render_to_string('./details_page/scan_data.html', {'selected_scan': selected_scan}),
                'statistics': selected_scan['statistics'],
                'scan_time': selected_scan['scan']['date'],
                'time_select_div': render_to_string('./details_page/select_times.html', {
                    'times': selected_scan['other_scans'], 
                    'act_time': selected_scan['scan']['time']
                }),
                'end_pagination': True if page >= paginator.num_pages else False,
            }
        elif request.POST['action'] == 'infinit_scroll':
            ajax_data = {
                'vuln_table': render_to_string('./details_page/vuln_table.html', {'vuln_page_obj': vuln_page_obj}),
                'end_pagination': True if page >= paginator.num_pages else False,
            }
        elif request.POST['action'] == 'search':
            ajax_data = {
                'vuln_table': render_to_string('./details_page/vuln_table.html', {'vuln_page_obj': vuln_page_obj}),
                'end_pagination': True if page >= paginator.num_pages else False,
           }
        elif request.POST['action'] == 'filter':
            ajax_data = {
                'vuln_table': render_to_string('./details_page/vuln_table.html', {'vuln_page_obj': vuln_page_obj}),
                'end_pagination': True if page >= paginator.num_pages else False,
            }
    return JsonResponse(ajax_data)
    


@login_required(login_url='/')
def redirect_workflow_id(request, workflow_id):
    # the correct scan
    scan = ScanData.objects.get(workflow_id=workflow_id)
    # get the correct scan date
    created_at = scan.created_at.strftime('%d-%m-%Y %H:%M:%S')
    repo_org = scan.repository.organization
    repo_name = scan.repository.name

    redirect_url = '/details/{}/{}?date={}'.format(repo_org, repo_name, created_at)
    return redirect(redirect_url)
