# Generated by Django 5.0.4 on 2024-04-13 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_is_admin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='client',
        ),
    ]
