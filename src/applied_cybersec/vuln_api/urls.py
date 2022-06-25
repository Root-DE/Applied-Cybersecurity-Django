from django.urls import path

from vuln_api.views import *

urlpatterns = [
    path('repo_notification/', repo_notification, name='repo_notification'),
]

# curl.exe -F "grype=@example_scans/grype.json" -F "syft=@example_scans/syft.json" -F "metadata=@example_scans/metadata.json" http://localhost:8000/api/send_scan_data/