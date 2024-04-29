import requests
import logging

from django.db.models import Count
from django.utils import timezone
from django.conf import settings
from scorm.models import ScormAssignment, UserScormMapping
from clients.models import Client

logger = logging.getLogger(__name__)


def check_assigned_scorm_validity(client_id, scorm_id) -> bool:
    # Get the client
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return False

    # Get the ScormAssignment for the client and the scorm_id
    try:
        assignment = ScormAssignment.objects.get(
            client=client, scorm_asset__scorm_id=scorm_id
        )
    except ScormAssignment.DoesNotExist:
        return False

    # Check if the current date is within the validity period of the assignment
    if assignment.validity_start_date <= timezone.now() <= assignment.validity_end_date:
        return True
    else:
        return False


def check_assigned_scorm_seats_limit(client_id, scorm_id) -> bool:
    # Get the client
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return False

    # Get the ScormAssignment for the client and the scorm_id
    try:
        assignment = ScormAssignment.objects.get(
            client=client, scorm_asset__scorm_id=scorm_id
        )
    except ScormAssignment.DoesNotExist:
        return False

    # Get the count of UserScormMapping for the assignment
    mapping_count = UserScormMapping.objects.filter(assignment=assignment).count()

    # Check if the count of UserScormMapping is less than or equal to the number of seats
    if mapping_count <= assignment.number_of_seats:
        return True
    else:
        return False


def create_user_on_cloudscorm(learner_id, bearer_token, **kwargs) -> dict:
    api_url = "https://cloudscorm.cloudnuv.com/user/signup"
    payload = {
        "email": learner_id + "@yopmail.com",
        "website": "LKD",
        "website_user_id": learner_id,
    }
    payload.update(kwargs)

    headers = {"Authorization": f"Bearer {bearer_token}"}

    try:
        response = requests.post(api_url, data=payload, headers=headers)
        response.raise_for_status()
        cloudscorm_user_data = response.json()

        if cloudscorm_user_data["error"]:
            print(
                f"Error creating user on CloudScorm: {cloudscorm_user_data['message']}"
            )
            return None

        return cloudscorm_user_data

    except requests.exceptions.RequestException as e:
        print(f"Error creating user on CloudScorm: {e}")
        return None


def construct_launch_url(scorm_id, cloudscorm_user_id) -> str:
    base_url = "https://cloudscorm.cloudnuv.com/course/"
    launch_url = f"{base_url}{scorm_id}/{cloudscorm_user_id}/online/0-0-0-0-0"
    return launch_url
