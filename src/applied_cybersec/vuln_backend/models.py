from enum import unique
import json
from django.db import models
from django.utils.timezone import now
import uuid

# Create your models here.
class Repositories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    # TODO: more info about the repository?

    class Meta:
        unique_together = ('organization', 'name')

class ScanData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=now, editable=False)
    repository = models.ForeignKey(Repositories, on_delete=models.CASCADE)
    workflow_id = models.BigIntegerField()
    grype_scan = models.JSONField()
    syft_scan = models.JSONField()

class Statistics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scan = models.ForeignKey(ScanData, on_delete=models.CASCADE)
    
    number_dependencies = models.IntegerField()
    number_vulnerabilities = models.IntegerField()
    number_vuln_critical = models.IntegerField()
    number_vuln_high = models.IntegerField()
    number_vuln_medium = models.IntegerField()
    number_vuln_low = models.IntegerField()
    number_vuln_negligible = models.IntegerField()
    number_vuln_unknown = models.IntegerField()

    # status = models.CharField(max_length=15)
    # TODO: more statistics?

class Artifacts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scan = models.ManyToManyField(ScanData)

    name = models.CharField(max_length=100, editable=False)
    version = models.CharField(max_length=100, editable=False)
    purl = models.CharField(max_length=250, editable=False)
    type = models.CharField(max_length=100, editable=False)
    cpes = models.JSONField(editable=False)
    licenses = models.JSONField(editable=False)

class Vulnerabilities(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vuln_id = models.CharField(max_length=100, editable=False)

    severity = models.CharField(max_length=100, editable=False)
    cvss = models.JSONField(editable=False)
    fix = models.JSONField(editable=False)
    description = models.TextField(editable=False, null=True)
    url = models.CharField(max_length=250, editable=False, null=True)

    scan = models.ManyToManyField(ScanData)
    artifact = models.ManyToManyField(Artifacts)