import logging

from django.shortcuts import render, get_object_or_404
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
from scorm.models import ScormAsset, ScormAssignment, ScormResponse, UserScormMapping
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
        * 400 Bad Request: Missing required data, invalid client identifier, invalid referring domain, invalid license.
        * 500 Internal Server Error: Failed to generate launch URL.
    """
    
    logger.info('Starting validate_and_launch')
    
    # Get the encrypted ID, referring URL, and learner ID from the request data
    encrypted_id = request.data.get("id")
    referring_url = request.data.get("referringurl")
    learner_id = request.data.get("learner_id")
    learner_name = request.data.get("name")
    
    logger.info(f'Received data: {encrypted_id}, {referring_url}, {learner_id}, {learner_name}')


    # Check if the required data is present
    if not all([encrypted_id, referring_url, learner_id, learner_name]):
        logger.error('Missing required data')
        return JsonResponse({"error": "Missing required data"}, status=400)

    # Decrypt the ID
    decrypted_id = decrypt_data(encrypted_id)

    # Split the decrypted ID to get the client ID and the SCORM ID
    client_id, scorm_id = decrypted_id.split("-")
    
    logger.info(f'Decrypted ID: {client_id}, {scorm_id}')

    # Get the client
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        logger.error('Invalid client identifier')
        return JsonResponse({"error": "Invalid client identifier"}, status=400)

    # Get the domain of the referring URL
    referring_domain = referring_url
    
    logger.info(f'Referring domain: {referring_domain}')

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
    logger.info(f"ClientUser: {client_user}")

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
    logger.info(f"UserScormMapping created for user: {client_user}")

    # Construct the launch URL
    launch_url = construct_launch_url(scorm_id, client_user.cloudscorm_user_id)
    logger.info(f"Launch URL: {launch_url}")

    # Return the launch URL
    if launch_url:
        return JsonResponse({"launch_url": launch_url})
    else:
        logger.info("Failed to generate launch URL")
        return JsonResponse({"error": "Failed to generate launch URL"}, status=500)