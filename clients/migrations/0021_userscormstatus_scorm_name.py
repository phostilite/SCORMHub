# Generated by Django 4.2.11 on 2024-06-03 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clients", "0020_userscormstatus_attempt_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userscormstatus",
            name="scorm_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
