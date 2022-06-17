from requests import delete
from rest_framework.views import APIView
from rest_framework.response import Response

import json
from datetime import datetime

from vuln_backend.models import *

# Create your views here.
class Receive_Scan_Data(APIView):
    def delete(self, request):
        # delete all database entries
        Vulnerabilities.objects.all().delete()
        Artifacts.objects.all().delete()
        ScanData.objects.all().delete()
        Repositories.objects.all().delete()
        Statistics.objects.all().delete()
        return Response({"status": "ok"})

    def get(self, request):

        return Response({"message": "Hello, World!"})

    def post(self, request):
        # TODO: check if permissions are correct
        # TODO: validate if the data is correct!
        try:
            # read the files and parse to json
            grype_file = request.FILES['grype'].read()
            grype_json = json.loads(grype_file)

            syft_file = request.FILES['syft'].read()
            syft_json = json.loads(syft_file)

            metadata_file = request.FILES['metadata'].read()
            metadata_json = json.loads(metadata_file)
        except Exception as e:
            print(e)
            return Response({"message": "Error parsing the files"})


        # get or create the repo entry
        repository = self.parse_repo_content(metadata_json)

        # add scan data to the database
        # --> get the timestamp of the scan
        created_at = datetime.strptime(metadata_json['created_at'], '%Y-%m-%d %H:%M:%S.%f') if 'created_at' in metadata_json else datetime.now()
        scan_entry = ScanData.objects.create(
            created_at=created_at,
            repository=repository,
            grype_scan=grype_json,
            syft_scan=syft_json
        )

        # add artifacts and vulnerabilities
        artifact_stats = self.parse_syft_scan(syft_json, scan_entry)
        vuln_stats = self.parse_grype_scan(grype_json, scan_entry)

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

    def parse_syft_scan(self, syft_json, scan_entry):
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

    def parse_grype_scan(self, grype_json, scan_entry):
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

    def parse_repo_content(self, metadata_json):
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