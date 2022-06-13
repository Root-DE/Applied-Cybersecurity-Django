from django.db import models
import uuid

# Create your models here.
class Repositories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    url = models.URLField()
    # TODO: more info about the repository?

class ArtifactData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    repository = models.ForeignKey(Repositories, on_delete=models.CASCADE)
    
    grype_scan = models.JSONField()

    # TODO: more artifact data to save? (sbom, etc.)


'''
SQL Querys:
WITH vulns AS (
  select jsonb_array_elements(grype_scan->'matches') as vuln from vuln_backend_artifactdata -- get the single vulnerability objects!
), cvss_data AS (
  select 
  CASE 
    WHEN vuln->'vulnerability' @> '{"namespace":"nvd"}'::jsonb THEN vuln->'vulnerability' -- nvd at first level
    ELSE (                                                                                -- nvd at another level
      select rvuln
      from jsonb_array_elements(vuln->'relatedVulnerabilities') as rvuln
      where rvuln->>'namespace' = 'nvd'
      limit 1
    )
  END as cvss_data 
from vulns
)

select cvss_data->>'id' as id, cvss_data->>'severity' as severity, cvss_data->'cvss' as cvss from cvss_data
'''