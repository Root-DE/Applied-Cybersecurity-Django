from requests import delete
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import sys
from django.views.decorators.csrf import csrf_exempt

import json
from datetime import datetime

from vuln_backend.models import *
from django.http import HttpResponse, HttpResponseBadRequest
import requests
import os
import zipfile
import shutil

@csrf_exempt
def repo_notification(request):
    if request.method == 'POST':
        headers={
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': 'token ' + os.environ['GITHUB_PAT'],
        }
        # get json
        try:
            json_data = json.loads(request.body)
        except ValueError as e:
            print(e)
            return HttpResponseBadRequest("Invalid JSON")
        
        # check if repo_org and repo_name are in the json
        if 'repo_org' not in json_data:
            return HttpResponseBadRequest('No repo_org in request')
        if 'repo_name' not in json_data:
            return HttpResponseBadRequest('No repo_name in request')

        # get repo url
        repo_org = json_data['repo_org']
        repo_name = json_data['repo_name']

        # check if owner is correct
        if repo_org.lower() != os.environ['GITHUB_ORG'].lower():
            return HttpResponseBadRequest("Repo not in scope")
        
        # get repos from owner
        r = requests.get('https://api.github.com/' + str(os.environ['USERS_OR_ORGS']).lower() + '/' + repo_org.lower() + '/repos', headers=headers)
        x = 'https://api.github.com/' + str(os.environ['USERS_OR_ORGS']).lower() + '/' + repo_org.lower() + '/repos'
        print(x)
        repos = r.json()

        # check if this repo is in the list
        in_scope = False
        for repo in repos:
            if repo['name'] == repo_name:
                in_scope = True
                break
        
        if not in_scope:
            return HttpResponseBadRequest("Repo not in scope")
        
        # get jobs from repo
        r = requests.get('https://api.github.com/repos/' + repo_org + '/' + repo_name + '/actions/artifacts', headers=headers)
        artifacts = r.json()
        # save with indent
        with open('artifacts.json', 'w') as f:
            json.dump(artifacts, f, indent=4)
        for artifact in artifacts['artifacts']:
            # print keys in artifact
            if artifact['name'] == 'scan':
                # check if this job is already in the database using the
                if ScanData.objects.filter(workflow_id=artifact['id']).exists():
                    print("scan already exists")
                    continue
                else:
                    print("new scan discovered")
                    # download the scan
                    r = requests.get(artifact['archive_download_url'], headers=headers)
                    # save the scan temporarily
                    workflow_id = str(artifact['id'])
                    with open('/tmp/' + workflow_id + '.zip', 'wb') as f:
                        f.write(r.content)
                    # unzip the scan
                    with zipfile.ZipFile('/tmp/' + workflow_id + '.zip', 'r') as zip_ref:
                        zip_ref.extractall('/tmp/' + workflow_id)
                    
                    # call create_db_entries
                    with open('/tmp/' + workflow_id + '/vuln.json', 'r') as f:
                        grype_file = f.read()
                    with open('/tmp/' + workflow_id + '/sbom.json', 'r') as f:
                        syft_file = f.read()

                    response = create_db_entries(grype_file, syft_file, json_data, workflow_id)
                    # delete the scan
                    shutil.rmtree('/tmp/' + workflow_id)
                    return HttpResponse(response.content, content_type='application/json')
        return HttpResponse("nice")
    else:
        # return invalid method
        return HttpResponseBadRequest("Invalid method")

def create_db_entries(grype_file, syft_file, metadata_file, workflow_id):
    # TODO: check if permissions are correct
    # TODO: validate if the data is correct!
    try:
        # read the files and parse to json
        grype_json = json.loads(grype_file)
        syft_json = json.loads(syft_file)
        metadata_json = metadata_file # already parsed to json

    except Exception as e:
        print(e)
        return Response({"message": "Error parsing the files"})


    # get or create the repository entry
    repository = parse_repo_content(metadata_json)

    # add scan data to the database
    # --> get the timestamp of the scan
    created_at = datetime.strptime(metadata_json['created_at'], '%Y-%m-%d %H:%M:%S.%f') if 'created_at' in metadata_json else datetime.now()
    scan_entry = ScanData.objects.create(
        created_at=created_at,
        repository=repository,
        workflow_id=int(workflow_id),
        grype_scan=grype_json,
        syft_scan=syft_json
    )

    # add artifacts and vulnerabilities
    artifact_stats = parse_syft_scan(syft_json, scan_entry)
    vuln_stats = parse_grype_scan(grype_json, scan_entry)

    # add an entry to the statistics table
    Statistics.objects.create(
        scan=scan_entry,
        number_dependencies=len(artifact_stats['artifacts']),
        number_vulnerabilities=len(vuln_stats['vulnerabilities']),
        number_vuln_critical=vuln_stats['Critical'],
        number_vuln_high=vuln_stats['High'],
        number_vuln_medium=vuln_stats['Medium'],
        number_vuln_low=vuln_stats['Low'],
        number_vuln_negligible=vuln_stats['Negligible'],
        number_vuln_unknown=vuln_stats['Unknown']
    )
    
    return Response({"status": "ok"})

def parse_syft_scan(syft_json, scan_entry):
    artifact_stats = {
        'artifacts': []
    }
    for artifact in syft_json['artifacts']:
        # update or create the artifact entry
        new_artifact, created = Artifacts.objects.update_or_create(
            name=artifact['name'],
            version=artifact['version'],
            defaults={
                'purl': artifact['purl'], 
                'type': artifact['type'], 
                'cpes': artifact['cpes'], 
                'licenses': artifact['licenses']
            }
        )

        # add artifact to scan
        new_artifact.scan.add(scan_entry)

        # add artifact to stats
        if (artifact['name'], artifact['version']) not in artifact_stats['artifacts']:
            artifact_stats['artifacts'].append((artifact['name'], artifact['version']))

    return artifact_stats

def parse_grype_scan(grype_json, scan_entry):
    vuln_stats = {
        'vulnerabilities': [],
        'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'Negligible': 0, 'Unknown': 0
    }
    for match in grype_json['matches']:
        vulnerability = match['vulnerability']
        # try to find the nvd entry
        if not vulnerability['namespace'] == 'nvd':
            for related_vuln in match['relatedVulnerabilities']:
                if related_vuln['namespace'] == 'nvd':
                    vulnerability = related_vuln
                    break
        
        # try to find the artifact entry
        artifact = Artifacts.objects.get(name=match['artifact']['name'], version=match['artifact']['version'])

        # update or create the vulnerability entry
        new_vulnerability, created = Vulnerabilities.objects.update_or_create(
            vuln_id=vulnerability['id'],
            defaults={
                'severity': vulnerability['severity'], 
                'cvss': vulnerability['cvss'], 
                'fix': match['vulnerability']['fix']
            }
        )

        # add scan and artifact entry to the vulnerability
        new_vulnerability.scan.add(scan_entry)
        new_vulnerability.artifact.add(artifact)

        # add vuln to stats 
        if vulnerability['id'] not in vuln_stats['vulnerabilities']:
            vuln_stats['vulnerabilities'].append(vulnerability['id'])
            try:
                vuln_stats[vulnerability['severity']] += 1
            except KeyError:
                vuln_stats['Unknown'] += 1

    return vuln_stats

def parse_repo_content(metadata_json):
    try:
        repository, created = Repositories.objects.get_or_create(
            url=metadata_json['repo_url'],
            defaults={'name': metadata_json['repo_name']}
        )
    except Exception as e:
        print(e)
        return Response({"message": "Error parsing the repository data"})
    print('created new Repository: ', created)
    return repository