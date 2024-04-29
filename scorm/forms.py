import os
from django.core.files import File
import logging

from django import forms
from .models import ScormAsset, ScormAssignment, ScormResponse
from clients.models import Client
from .utils import generate_client_scorm_file, encrypt_data, decrypt_data

logger = logging.getLogger(__name__)


class ScormUploadForm(forms.ModelForm):
    class Meta:
        model = ScormAsset
        fields = ["title", "description", "category", "duration", "scorm_file"]
        widgets = {"scorm_file": forms.FileInput()}


class AssignSCORMForm(forms.ModelForm):
    scorms = forms.ModelMultipleChoiceField(
        queryset=ScormAsset.objects.all(), widget=forms.CheckboxSelectMultiple
    )
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(), widget=forms.HiddenInput
    )
    validity_start_date = forms.DateTimeField(widget=forms.DateInput, required=False)
    validity_end_date = forms.DateTimeField(widget=forms.DateInput, required=False)

    class Meta:
        model = ScormAssignment
        fields = ["number_of_seats", "validity_start_date", "validity_end_date"]

    def save(self, client, commit=True):
        selected_scorms = self.cleaned_data["scorms"]
        number_of_seats = self.cleaned_data["number_of_seats"]
        validity_start_date = self.cleaned_data["validity_start_date"]
        validity_end_date = self.cleaned_data["validity_end_date"]

        assignments = []
        for scorm in selected_scorms:
            assignment = ScormAssignment(
                scorm_asset=scorm,
                client=client,
                number_of_seats=number_of_seats,
                validity_start_date=validity_start_date,
                validity_end_date=validity_end_date,
            )

            response = ScormResponse.objects.get(asset=scorm)

            encrypted_id = encrypt_data(client.id, response.scorm)
            logger.info(f"Encrypted ID: {encrypted_id}")
            client_specific_data = {"id": encrypted_id, "scorm_title": scorm.title}
            client_scorm_file_path = generate_client_scorm_file(
                scorm.scorm_file, client_specific_data
            )

            # Log the decrypted ID for verification
            decrypted_id = decrypt_data(encrypted_id)
            logger.info(f"Decrypted ID: {decrypted_id}")

            # Save the client-specific SCORM file in the ScormAsset model
            with open(client_scorm_file_path, "rb") as client_scorm_file:
                assignment.client_scorm_file.save(
                    os.path.basename(client_scorm_file_path), File(client_scorm_file)
                )

            if commit:
                assignment.save()
                scorm.save()  # Save the ScormAsset model after updating the scorm_file field
            assignments.append(assignment)

        return assignments
