import logging
import json
import requests
import base64
import time
import random
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from urllib.parse import urlparse
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema

from clients.models import Client, ClientUser
from scorm.models import ScormAsset, ScormAssignment, ScormResponse, UserScormMapping, Course, Module
from scorm.utils import decrypt_data
from api.serializers import (
    ClientSerializer,
    ClientUserSerializer,
    ValidateAndLaunchRequest,
    ValidateAndLaunchResponse,
)
from .utils import (
    check_assigned_scorm_validity,
    create_user_on_cloudscorm,
    construct_launch_url,
    check_assigned_scorm_seats_limit,
)

logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method="post",
    request_body=ValidateAndLaunchRequest,
    responses={
        200: ValidateAndLaunchResponse(),
        400: "Bad Request",
        500: "Internal Server Error",
    },
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def validate_and_launch(request):
    """
    Validates a learner's access to a SCORM package, creates a user on CloudScorm if needed, and returns a launch URL.

    - This endpoint receives a POST request containing encrypted data representing the client and SCORM IDs, along with learner information.
    - It decrypts the data, validates the client, referring domain, and SCORM assignment, and creates or retrieves the learner's information.
    - If necessary, it synchronizes the learner with CloudScorm. Finally, it constructs a launch URL for the SCORM package and returns it.

    Args:
        request (HTTPRequest): The incoming request object containing:
            * id (str): Encrypted ID containing client ID and SCORM ID.
            * referringurl (str): The referring domain of the learner.
            * learner_id (str): The unique learner identifier.
            * name (str): The first name of the learner.

    Returns:
        JsonResponse: A JSON response with either:
            * launch_url (str): The URL to launch the SCORM package.
            * error (str): An error message if validation or launch URL generation fails.

    Error Codes:
        * 400 Bad Request: MissLing required data, invalid client identifier, invalid referring domain, invalid license.
        * 500 Internal Server Error: Failed to generate launch URL.
    """
        
    # Get the encrypted ID, referring URL, and learner ID from the request data
    encrypted_id = request.data.get("id")
    referring_url = request.data.get("referringurl")
    learner_id = request.data.get("learner_id")
    learner_name = request.data.get("name")
    
    # Check if the required data is present
    if not all([encrypted_id, referring_url, learner_id, learner_name]):
        logger.error('Missing required data')
        return JsonResponse({"error": "Missing required data"}, status=400)

    # Decrypt the ID
    decrypted_id = decrypt_data(encrypted_id)

    # Split the decrypted ID to get the client ID and the SCORM ID
    client_id, scorm_id = decrypted_id.split("-")
    
    # Get the client
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        logger.error('Invalid client identifier')
        return JsonResponse({"error": "Invalid client identifier"}, status=400)

    # Get the domain of the referring URL
    referring_domain = referring_url
    
    # Get the list of valid domains for the client
    valid_domains = client.domains.split(",")

    # Check if the referring domain is in the list of valid domains for the client
    if referring_domain not in valid_domains:
        logger.info("Invalid referring domain")
        return JsonResponse({"error": "Invalid referring domain"}, status=400)

    # Check if the SCORM assignment is valid
    if not check_assigned_scorm_validity(client_id, scorm_id):
        logger.info("License invalid")
        return JsonResponse({"error": "License invalid"}, status=400)

    # Check if the SCORM assignment seats limit is not exceeded
    if not check_assigned_scorm_seats_limit(client_id, scorm_id):
        logger.info("Seats limit exceeded")
        return JsonResponse({"error": "Seats limit exceeded"}, status=400)

    # Find or Create the ClientUser
    client_user, _ = ClientUser.objects.get_or_create(
        learner_id=learner_id, client=client, defaults={"first_name": learner_name}
    )

    # CloudScorm Sync
    bearer_token = settings.API_TOKEN1
    if not client_user.cloudscorm_user_id:
        cloudscorm_user_data = create_user_on_cloudscorm(learner_id, bearer_token)
        logger.info(f'CloudScorm User Data: {cloudscorm_user_data}')
        client_user.cloudscorm_user_id = cloudscorm_user_data["user_id"]
        client_user.save()
        
    scorm_asset = get_object_or_404(ScormAsset, scorm_id=scorm_id)
    assignment = get_object_or_404(ScormAssignment, scorm_asset=scorm_asset)

    # Create a UserScormMapping  
    UserScormMapping.objects.get_or_create(
        user=client_user, 
        assignment=assignment
    )

    # Construct the launch URL
    launch_url = construct_launch_url(scorm_id, client_user.cloudscorm_user_id)

    # Return the launch URL
    if launch_url:
        return JsonResponse({"launch_url": launch_url, "cloudscorm_user_id": client_user.cloudscorm_user_id})
    else:
        logger.info("Failed to generate launch URL")
        return JsonResponse({"error": "Failed to generate launch URL"}, status=500)
    
def get_scorm_data(request, client_id, scorm_id):
    try:
        assignment = ScormAssignment.objects.get(client_id=client_id, scorm_asset_id=scorm_id)
        scorm = assignment.scorm_asset
        data = {
            "course_title": scorm.title,
            "cover_photo": request.build_absolute_uri(scorm.cover_photo.url),
            "short_description": scorm.description,
            "long_description": '',
            "modules": [{"type": 'scorm', "scorm_title": scorm.title, "file": request.build_absolute_uri(scorm.scorm_file.url)}]
        }
        return JsonResponse(data, safe=False)
    except ScormAssignment.DoesNotExist:
        logger.exception("Scorm assignment not found")
        return JsonResponse({"error": "Scorm assignment not found"}, status=404)
    except Exception as e:
        logger.exception("An error occurred")
        return JsonResponse({"error": str(e)}, status=400)


@require_POST
def sync_courses(request):
    try:
        # Validate and sanitize the request data
        data = json.loads(request.body)
        client_id = data.get('clientId')
        scorm_id = data.get('scormId')

        if not client_id or not scorm_id:
            return JsonResponse({"error": "Missing required fields (clientId, scormId)"}, status=400)

        client = get_object_or_404(Client, id=client_id)
        scorm = get_object_or_404(ScormAsset, id=scorm_id)

        # Check if a Course object already exists for the given SCORM asset
        existing_course = Course.objects.filter(scorm_assets=scorm).first()

        if existing_course:
            course = existing_course
            course.title = data.get('course_title', course.title)
            course.code = str(int(time.time())) + str(random.randint(100, 999))
            course.cover_photo = data.get('cover_photo', course.cover_photo)
            course.short_description = data.get('short_description', course.short_description)
            course.long_description = data.get('long_description', course.long_description)
        else:
            unique_code = str(int(time.time())) + str(random.randint(100, 999))
            course = Course.objects.create(
                title=data.get('course_title', ''),
                code=unique_code,
                cover_photo=data.get('cover_photo', ''),
                short_description=data.get('short_description', ''),
                long_description=data.get('long_description', ''),
            )
            course.scorm_assets.add(scorm)

        if not course.syncing_status:
            course.modules.all().delete()  # Delete existing modules

            for module_data in data.get('modules', []):
                try:
                    Module.objects.create(
                        course=course,
                        type=module_data.get('type', 'scorm'),
                        title=module_data.get('scorm_title', ''),
                        file=module_data.get('file', '')
                    )
                except ValidationError as e:
                    logger.error(f"Validation error while creating module: {e}")

            lms_url = f"{client.lms_url}/api/v1/course-create"
            LMS_API_KEY = client.lms_api_key
            LMS_API_SECRET = client.lms_api_secret

            credentials = base64.b64encode(f"{LMS_API_KEY}:{LMS_API_SECRET}".encode('utf-8')).decode('utf-8')
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {credentials}',
            }
            response = requests.post(lms_url, headers=headers, data=json.dumps(data))

            if response.status_code == 201:
                course.syncing_status = True
                course.save()
                return JsonResponse({"message": "Course created and synced successfully"}, status=201)
            else:
                logger.error(f"Failed to sync course to client LMS. Status code: {response.status_code}, Response: {response.text}")
                return JsonResponse({"error": f"Failed to sync course to client LMS. Status code: {response.status_code}, Response: {response.text}"}, status=400)

        else:
            return JsonResponse({"message": "Course already synced"}, status=200)

    except Exception as e:
        logger.exception("An error occurred in sync_courses")
        return JsonResponse({"error": str(e)}, status=400)