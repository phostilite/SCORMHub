# Generated by Django 5.0.4 on 2024-04-11 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0005_client_created_at_client_scorm_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScormAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('category', models.CharField(blank=True, max_length=50)),
                ('duration', models.CharField(blank=True, max_length=50)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('access_validity_period', models.IntegerField(blank=True, default=365)),
                ('license_seats', models.IntegerField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('scorm_id', models.IntegerField(unique=True)),
                ('clients', models.ManyToManyField(to='clients.client')),
            ],
        ),
    ]
