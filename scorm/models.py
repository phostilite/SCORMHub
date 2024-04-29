from django.db import models
from clients.models import Client, ClientUser


class ScormAsset(models.Model):
    """
    Represents a SCORM asset.

    Attributes:
        title (str): The title of the asset.
        description (str): The description of the asset.
        category (str): The category of the asset.
        duration (datetime.timedelta): The duration of the asset.
        upload_date (datetime.datetime): The date and time when the asset was uploaded.
        access_validity_period (int): The validity period of the asset in days.
        license_seats (int): The number of license seats for the asset.
        is_deleted (bool): Indicates whether the asset is deleted or not.
        scorm_id (int): The unique identifier for the SCORM asset.
        clients (ManyToManyField): The clients associated with the asset.
        scorm_file (FileField): The uploaded SCORM file.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, blank=True)
    duration = models.DurationField(blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    scorm_id = models.IntegerField(unique=True, null=True)
    scorm_file = models.FileField(upload_to="scorm_uploads_zipped/")

    def __str__(self):
        return self.title


class ScormResponse(models.Model):
    """
    Represents a response to a SCORM asset.

    Attributes:
        asset (ScormAsset): The SCORM asset associated with the response.
        status (bool): The status of the response.
        message (str): The message associated with the response.
        scormdir (str): The directory of the SCORM package.
        full_path_name (str): The full path name of the response.
        size (int): The size of the response.
        zippath (str): The path of the ZIP file.
        zipfilename (str): The name of the ZIP file.
        extension (str): The extension of the response file.
        filename (str): The name of the response file.
        reference (str): The reference of the response.
        scorm (str): The SCORM version.

    """
    asset = models.OneToOneField(
        ScormAsset, on_delete=models.CASCADE, related_name="response"
    )
    status = models.BooleanField(null=True)
    message = models.TextField(null=True)
    scormdir = models.TextField(null=True)
    full_path_name = models.TextField(null=True)
    size = models.BigIntegerField(null=True)
    zippath = models.TextField(null=True)
    zipfilename = models.TextField(null=True)
    extension = models.CharField(max_length=10, null=True)
    filename = models.TextField(null=True)
    reference = models.TextField(null=True)
    scorm = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.asset.title


class ScormAssignment(models.Model):
    """
    Represents a Scorm Assignment.

    Attributes:
        client (ForeignKey): The client associated with the assignment.
        scorm_asset (ForeignKey): The Scorm asset associated with the assignment.
        date_assigned (DateTimeField): The date and time when the assignment was created.
        number_of_seats (IntegerField): The number of seats available for the assignment.
        validity_start_date (DateTimeField): The start date and time of the assignment's validity period.
        validity_end_date (DateTimeField): The end date and time of the assignment's validity period.
        client_scorm_file (FileField): The uploaded Scorm file associated with the assignment.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    scorm_asset = models.ForeignKey(ScormAsset, on_delete=models.CASCADE)
    date_assigned = models.DateTimeField(auto_now_add=True)
    number_of_seats = models.IntegerField(default=1)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    client_scorm_file = models.FileField(upload_to='client_scorm_files/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.client} - {self.scorm_asset}"
    
class UserScormMapping(models.Model):
    """
    Represents the mapping between a user and a SCORM assignment.
    """

    user = models.ForeignKey(ClientUser, on_delete=models.CASCADE)
    assignment = models.ForeignKey(ScormAssignment, on_delete=models.CASCADE)