# Generated by Django 4.0.5 on 2022-06-16 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vuln_backend', '0002_artifacts_scandata_statistics_vulnerabilities_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vulnerabilities',
            name='artifact',
        ),
        migrations.AddField(
            model_name='vulnerabilities',
            name='artifact',
            field=models.ManyToManyField(to='vuln_backend.artifacts'),
        ),
    ]