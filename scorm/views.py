import os
import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    FileResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError,
)

import requests

from clients.models import Client
from accounts.decorators import allowed_users

from .forms import ScormUploadForm, AssignSCORMForm
from .models import ScormAsset, ScormResponse, ScormAssignment

logger = logging.getLogger(__name__)


@login_required
@allowed_users(allowed_roles=["coreadmin"])
def upload_scorm_view(request) -> HttpResponse:
    """
    View function for uploading a SCORM file.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        ValidationError: If the file size exceeds the limit.
        ValueError: If the 'scorm_id' is None or cannot be converted to an integer.
        Exception: If there is an error during file upload.

    """
    form = ScormUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            asset = form.save(commit=False)
            try:
                scorm_file = request.FILES["scorm_file"]

                if scorm_file.size > settings.MAX_UPLOAD_SIZE:
                    raise ValidationError("File size exceeds the limit")

                headers = {
                    "Authorization": f"Bearer {settings.API_TOKEN1}",
                }

                data = {
                    "file": scorm_file,
                }

                response = requests.post(
                    settings.API_URL,
                    headers=headers,
                    files=data,
                    verify=True,
                    timeout=100,
                )

                response_data = None

                content_type = response.headers.get("content-type")

                if content_type.startswith(
                    "application/json"
                ) or content_type.startswith("text/html"):
                    try:
                        response_data = response.content.decode("utf-8")
                        response_data = json.loads(response_data)
                        logger.debug(
                            "Response: %s", json.dumps(response_data, indent=4)
                        )
                    except json.JSONDecodeError:
                        logger.error("Error decoding JSON from response")
                        response_data = None
                else:
                    logger.debug("Response: %s", response.content)

                if (
                    response.status_code == 200
                    and response_data is not None
                    and response_data.get("status") is True
                ):
                    logger.info("File uploaded successfully")

                    scorm_id = response_data.get("scorm")
                    if scorm_id is not None:
                        try:
                            scorm_id = int(scorm_id)

                            if ScormResponse.objects.filter(scorm=scorm_id).exists():
                                logger.error("A SCORM file with the same ID already exists")
                                return HttpResponseBadRequest("A SCORM file with the same ID already exists")
                            
                            asset.scorm_id = scorm_id
                            asset.save()

                            try:
                                ScormResponse.objects.create(
                                    asset=asset,
                                    status=response_data.get("status"),
                                    message=response_data.get("message"),
                                    scormdir=response_data.get("scormdir"),
                                    full_path_name=response_data.get("full_path_name"),
                                    size=response_data.get("size"),
                                    zippath=response_data.get("zippath"),
                                    zipfilename=response_data.get("zipfilename"),
                                    extension=response_data.get("extension"),
                                    filename=response_data.get("filename"),
                                    reference=response_data.get("reference"),
                                    scorm=response_data.get("scorm"),
                                )
                                logger.info("ScormResponse object created successfully")
                            except Exception as e:
                                logger.exception(
                                    "Error creating ScormResponse object: %s", e
                                )
                                raise
                        except ValueError:
                            logger.error("scorm_id cannot be converted to an integer")
                            raise
                    else:
                        logger.error("scorm_id is None")
                        raise ValueError("scorm_id is None")
                else:
                    logger.error(
                        "Failed to upload file. Status code: %s", response.status_code
                    )
                    if response_data is not None:
                        logger.error("Response: %s", response.text)
                    raise Exception("Failed to upload file")

                return redirect("scorm-dashboard")
            except Exception as e:
                logger.exception("An error occurred:")
                return HttpResponseBadRequest("An error occurred during file upload")
        else:
            logger.debug("Form errors: %s", form.errors.as_json())
            return HttpResponseBadRequest("Invalid form data")
    return render(request, "scorm/upload_scorm.html", {"form": form})

@login_required
@allowed_users(allowed_roles=["coreadmin"])
def scorm_dashboard_view(request) -> HttpResponse:
    """
    Renders the SCORM dashboard view.

    This view requires the user to be authenticated. If the user is not authenticated,
    they will be redirected to the admin login page.

    The function fetches all SCORM assets from the database and renders the 'scorm-dashboard.html'
    template with the fetched SCORM assets.

    Returns:
        A rendered HTML response containing the SCORM dashboard view.

    Raises:
        ObjectDoesNotExist: If there is an error fetching the SCORM assets from the database.
    """
    if not request.user.is_authenticated:
        return redirect("admin-login")

    try:
        scorms = ScormAsset.objects.all()
    except ObjectDoesNotExist:
        messages.error(request, "Error fetching scorms")
        scorms = None
    return render(request, "scorm/scorm-dashboard.html", {"scorms": scorms})


@login_required
@allowed_users(allowed_roles=["coreadmin"])
def get_all_scorms(request) -> HttpResponse:
    """
    Retrieve all SCORM assets and render them in the 'get_all_scorms.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.

    Raises:
        None

    """
    try:
        scorms = ScormAsset.objects.all()
        form = AssignSCORMForm()
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        scorms = []
        form = None
    return render(request, "scorm/get_all_scorms.html", {"scorms": scorms, "form": form})


@login_required
@allowed_users(allowed_roles=["coreadmin"])
def assign_scorm(request, client_id) -> HttpResponse:
    """
    Assigns a SCORM package to a client.

    Args:
        request (HttpRequest): The HTTP request object.
        client_id (int): The ID of the client.

    Returns:
        HttpResponse: The HTTP response.

    Raises:
        Http404: If the client with the specified ID does not exist.
    """
    client = get_object_or_404(Client, pk=client_id)
    form = None
    try:
        if request.method == "POST":
            form = AssignSCORMForm(request.POST)
            if form.is_valid():
                logger.info("Form is valid. Saving...")
                form.save(client)
                logger.info(f"Successfully saved ScormAssignment for client_id={client_id}")
                return redirect("client-details", client_id=client_id)
        else:
            form = AssignSCORMForm(initial={'client': client})
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
    return render(
        request, "clients/client_details.html", {"form": form, "client": client}
    )

@login_required
@allowed_users(allowed_roles=["coreadmin", "clientadmin"])
def download_scorm(request, client_id, scorm_id) -> HttpResponse:
    try:
        client = get_object_or_404(Client, pk=client_id)
        scorm = get_object_or_404(ScormAsset, pk=scorm_id)

        assignment = ScormAssignment.objects.filter(
            client=client, scorm_asset=scorm
        ).first()

        if not assignment:
            raise PermissionDenied("You do not have access to this SCORM")

        if not os.path.exists(assignment.client_scorm_file.path):
            raise Http404("File not found")

        file = open(assignment.client_scorm_file.path, "rb")
    except (Http404, PermissionDenied):
        raise
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)

    response = FileResponse(file, content_type="application/zip")
    filename = f"{client.first_name}_{scorm.title}.zip"  
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response

@login_required
@allowed_users(allowed_roles=["coreadmin", "clientadmin"])
def download_scorm_via_api(request, client_id, scorm_id) -> HttpResponse:
   pass