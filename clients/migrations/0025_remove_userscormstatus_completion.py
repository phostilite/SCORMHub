# Generated by Django 4.2.11 on 2024-06-03 11:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("clients", "0024_remove_userscormstatus_scorm"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userscormstatus",
            name="completion",
        ),
    ]
