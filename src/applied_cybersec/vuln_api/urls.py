from django.urls import path

from vuln_api.views import *

urlpatterns = [
    path('send_zip/', Receive_Artifacts.as_view(), name='recieve_artifact'),
]

# curl.exe -X Post -H "content-type: application/json;" -d @example_scans/grype_from_sbom.json http://localhost:8000/api/send_zip/
