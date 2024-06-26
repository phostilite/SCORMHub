# Generated by Django 4.2.11 on 2024-05-16 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clients", "0014_rename_scorm_user_id_clientuser_cloudscorm_user_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="lms_api_key",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="client",
            name="lms_api_key_secret",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="client",
            name="lms_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]
