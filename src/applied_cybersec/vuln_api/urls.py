from django.urls import path

from vuln_api.views import *

urlpatterns = [
    path('send_scan_data/', Receive_Scan_Data.as_view(), name='receive_scan_data'),
]

# curl.exe -F "grype=@example_scans/grype.json" -F "syft=@example_scans/syft.json" -F "metadata=@example_scans/metadata.json" http://localhost:8000/api/send_scan_data/