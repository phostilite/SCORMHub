# Generated by Django 5.0.4 on 2024-04-13 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_customuser_is_client_admin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='is_admin',
            new_name='is_core_admin',
        ),
    ]
