# Generated by Django 5.0.4 on 2024-04-13 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0007_remove_client_scorm_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='contact_email',
            new_name='email',
        ),
    ]
