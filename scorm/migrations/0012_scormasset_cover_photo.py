# Generated by Django 4.2.11 on 2024-05-21 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scorm", "0011_course_module"),
    ]

    operations = [
        migrations.AddField(
            model_name="scormasset",
            name="cover_photo",
            field=models.ImageField(
                blank=True, null=True, upload_to="scorm_uploads/cover_photos/"
            ),
        ),
    ]