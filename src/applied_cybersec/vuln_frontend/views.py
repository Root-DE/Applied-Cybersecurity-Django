from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.paginator import Paginator

from vuln_backend.models import *

# Create your views here.

@login_required(login_url='/')
def dashboard(request):
    # ------------------------------------
    # get all the data we want to display
    # ------------------------------------
    # get some global statistics
    # TODO

    # get the newest statistics for each repository
    repositories = Repositories.objects.all().order_by('name')
    scan_data = []
    for repository in repositories:
        latest_scan = ScanData.objects.filter(repository=repository).latest('created_at')
        statistics = Statistics.objects.filter(scan=latest_scan).values().first()
        scan_data.append({
            'repo_org': repository.organization,
            'repo_name': repository.name,
            'repo_id': repository.id,
            'scan_date': str(latest_scan.created_at),
            'workflow_id': latest_scan.workflow_id,
            'statistics': statistics
        })


    return render(request, 'dashboard.html', {"name": request.user.username, 'scan_data': scan_data})

def error_500(request):
    return render(request, '500.html')

@login_required(login_url='/')
def download(self, result_type, repoid, created_at):
    filename = result_type + "_" + str(repoid) + "_" + str(created_at)
    scan_data = ScanData.objects.get(created_at=created_at, repository=repoid)
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


    # get the selected date
    actual_date = None
    if request.GET.get('date'):
        actual_date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d %H:%M:%S')
        actual_date = timezone.make_aware(actual_date, timezone.get_current_timezone())

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

    # get the statistics of the selected scan
    selected_scan['statistics'] = statistics.filter(scan=selected_scan['scan']['id']).values().first()
    
    # get the vulnerabilities for the selected scan
    vulnerabilities = Vulnerabilities.objects.filter(scan=selected_scan['scan']['id'])
    # apply pagination
    paginator = Paginator(vulnerabilities, 1)
    # try to get the page number from the url
    page = request.GET.get('page', 1)
    # adjust the elided pages
    vuln_page_obj = paginator.get_page(page)
    vuln_page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page)

    scans = scans.values('id', 'created_at', 'workflow_id', 'repository_id')

    # create dict for the graph visualization
    graph_data = {
        'created_at': [],
        'low': [],
        'medium': [],
        'high': [],
        'critical': [],
    }

    statistics = statistics.values()

    for scan in scans:
        # format date to epoch time
        # scan['created_at'] = int(scan['created_at'].timestamp())
        graph_data["created_at"].append(scan["created_at"].strftime("%Y-%m-%dT%H:%M:%S"))

    for stat in statistics:
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
        'page': page,
        'paginator': paginator,
        'vuln_page_obj': vuln_page_obj,
        'graph_data': graph_data,
    }

    # ====================================
    # check if it is an ajax request
    # ====================================
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        # check if a new scan is selected or pagination is used
        if request.method == 'POST' and 'action' in request.POST:
            if request.POST['action'] == 'select_scan':
                ajax_data = {'vuln_table': render_to_string('./details_page/vuln_table.html', {'vulnerabilities': vulnerabilities})}
            elif request.POST['action'] == 'paginate':
                ajax_data = {
                    'vuln_table': render_to_string('./details_page/vuln_table.html', {'vulnerabilities': vuln_page_obj}),
                    'pagination_div': render_to_string('./details_page/pagination.html', {'repo': repo, 'vuln_page_obj': vuln_page_obj})
                }
        return JsonResponse(ajax_data)
    
    return render(request, './details_page/details.html', context)


@login_required(login_url='/')
def refresh_details_table(request):
    if request.is_ajax():
        print('AJAX RECEIVED')
    pass
