from rest_framework.views import APIView
from rest_framework.response import Response

from vuln_backend.models import Repositories, ArtifactData

# Create your views here.
class Receive_Artifacts(APIView):
    def post(self, request):
        # TODO: check if permissions are correct
        # TODO: validate if the data is correct!
        repo_name = 'Test_Repo'
        repo_url = 'https://github.com/test/test'
        repo, created = Repositories.objects.get_or_create(name=repo_name, url=repo_url)
        print(repo)
        try:
            artifact_data = ArtifactData.objects.create(repository=repo, grype_scan=request.data)
            artifact_data.save()
        except Exception as e:
            print(e)
        
        return Response({"status": "ok"})
