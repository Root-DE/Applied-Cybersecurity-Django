from enum import unique
import json
from django.db import models
from django.utils.timezone import now
import uuid

# Create your models here.
class Repositories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    url = models.URLField(unique=True)
    # TODO: more info about the repository?

class ScanData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=now, editable=False)
    repository = models.ForeignKey(Repositories, on_delete=models.CASCADE)
    
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

    name = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    purl = models.CharField(max_length=250, unique=True)
    type = models.CharField(max_length=100)
    cpes = models.JSONField()
    licenses = models.JSONField()

    class Meta:
        unique_together = ('name', 'version')

class Vulnerabilities(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vuln_id = models.CharField(max_length=100, unique=True)
    scan = models.ManyToManyField(ScanData)

    severity = models.CharField(max_length=100)
    cvss = models.JSONField()
    fix = models.JSONField()
    artifact = models.ManyToManyField(Artifacts)