from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.http import JsonResponse
from django.urls import reverse
import requests
import json
from .models import ClientUser, Client
from scorm.utils import encrypt_data, decrypt_data
from django.core.exceptions import ObjectDoesNotExist

from scorm.models import ScormAssignment, ScormAsset
from accounts.decorators import allowed_users

# from .tasks import user_logged_in_task, user_logged_out_task
from .forms import ClientCreationForm, ClientUpdateForm, ClientLoginForm, ClientUserForm
from .models import Client, ClientUser

import logging

logger = logging.getLogger(__name__)

@login_required
@allowed_users(allowed_roles=["coreadmin"])
def create_client_view(request):
    """
    View function for creating a client.

    This view function handles the creation of a client. It checks if the user is an admin,
    validates the form data, saves the client, and redirects to the client dashboard.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    if request.method == "POST":
        form = ClientCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Client created successfully")
            return redirect("client-dashboard")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ClientCreationForm()
    return render(request, "clients/create_client.html", {"form": form})


@login_required
def client_dashboard_view(request):
    """
    View function for the client dashboard.

    This view displays the client dashboard page, which shows a list of all clients.
    Only authenticated users can access this page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.

    Raises:
        None

    """
    if not request.user.is_authenticated:
        return redirect("admin-login")

    try:
        clients = Client.objects.all()
    except ObjectDoesNotExist:
        messages.error(request, "Error fetching clients")
        clients = None

    return render(request, "clients/client_dashboard.html", {"clients": clients})


@login_required
def client_update_view(request, client_id):
    """
    Update the client information.

    Args:
        request (HttpRequest): The HTTP request object.
        client_id (int): The ID of the client to update.

    Returns:
        HttpResponse: The HTTP response.

    Raises:
        Http404: If the client with the specified ID does not exist.

    """
    if not request.user.is_core_admin:
        return redirect("client-dashboard")

    client = get_object_or_404(Client, id=client_id)

    if request.method == "POST":
        if (
            "HTTP_X_REQUESTED_WITH" in request.META
            and request.META["HTTP_X_REQUESTED_WITH"] == "XMLHttpRequest"
        ):  # Handle AJAX form submission
            form = ClientUpdateForm(request.POST, instance=client)
            if form.is_valid():
                form.save()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "errors": form.errors})
        else:
            form = ClientUpdateForm(request.POST, instance=client)
            if form.is_valid():
                form.save()
                messages.success(request, "Client updated successfully")
                return redirect("client-dashboard")
    else:
        form = ClientUpdateForm(instance=client)

    return render(request, "clients/client_dashboard.html", {"form": form})


@login_required
def get_client_details(request, client_id):
    """
    Retrieve the details of a client based on the provided client_id.

    Args:
        request (HttpRequest): The HTTP request object.
        client_id (int): The ID of the client to retrieve details for.

    Returns:
        JsonResponse: A JSON response containing the client details.

    Raises:
        Client.DoesNotExist: If the client with the provided client_id does not exist.
    """
    client = Client.objects.get(pk=client_id)
    data = {
        "first_name": client.first_name,
        "last_name": client.last_name,
        "company": client.company,
        "email": client.email,
        "contact_phone": client.contact_phone,
        "domains": client.domains,
        "lms_url": client.lms_url,
        "lms_api_key": client.lms_api_key,
        "lms_api_secret": client.lms_api_secret,
    }
    return JsonResponse(data)


@login_required
@allowed_users(allowed_roles=["coreadmin"])
def client_details_view_for_coreadmin(request, client_id):
    """
    View function for displaying the details of a client.

    Args:
        request (HttpRequest): The HTTP request object.
        client_id (int): The ID of the client to display details for.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.

    Raises:
        Http404: If the client with the specified ID does not exist.

    """
    client = get_object_or_404(Client, id=client_id)
    assignments = ScormAssignment.objects.filter(client=client)
    return render(
        request,
        "clients/client_details.html",
        {"client": client, "assignments": assignments},
    )

@login_required
@allowed_users(allowed_roles=["clientadmin"])
def client_details_view_for_clientadmin(request, client_id):
    """
    View function for displaying the details of a client.

    Args:
        request (HttpRequest): The HTTP request object.
        client_id (int): The ID of the client to display details for.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.

    Raises:
        Http404: If the client with the specified ID does not exist.
        PermissionDenied: If the logged-in user is not allowed to view the client's details.

    """
    client = get_object_or_404(Client, id=client_id)
    
    if request.user.client.id != client.id:
        raise PermissionDenied
    
    assignments = ScormAssignment.objects.filter(client=client)
    return render(
        request,
        "clients/client_details_for_clientadmin.html",
        {"client": client, "assignments": assignments},
    )

def client_login_view(request):
    """
    View function for handling the client login.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    
    if request.user.is_authenticated and request.user.is_client_admin:
        return redirect("client-details-clientadmin", client_id=request.user.client.id)
    
    if request.method == "POST":
        form = ClientLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_client_admin:
                    login(request, user)
                    # user_logged_in_task.delay(user.id)
                    return redirect("client-details-clientadmin", client_id=user.client.id)
                else:
                    messages.error(
                        request, "This account doesn't have client admin permissions."
                    )
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = ClientLoginForm()
    return render(request, "clients/login.html", {"form": form})

def client_logout_view(request):
    """
    Logs out the client user and redirects to the client login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: A redirect response to the client login page.
    """
    user_id = request.user.id
    logout(request)
    # user_logged_out_task.delay(user_id)
    return redirect("client-login")


@login_required
@allowed_users(allowed_roles=["coreadmin"])
def users_list_for_coreadmin(request, client_id):
    """
    View function for displaying the list of users associated with a specific client.

    Args:
        request (HttpRequest): The HTTP request object.
        client_id (int): The ID of the client.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.

    """
    try:
        client = get_object_or_404(Client, id=client_id)
        users = ClientUser.objects.filter(client_id=client_id)
        messages.success(request, 'Users fetched successfully.')
    except Client.DoesNotExist:
        messages.error(request, 'Client does not exist.')
        return redirect(request.META.get('HTTP_REFERER', 'default_if_referer_not_found'))
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', 'default_if_referer_not_found'))

    return render(request, "clients/users_coreadmin.html", {"users": users, "client": client})


@login_required
@allowed_users(allowed_roles=["clientadmin"])
def users_list_for_clientadmin(request, client_id):
    """
    View function for displaying the list of users associated with the client admin.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.

    """
    try:
        client = get_object_or_404(Client, id=client_id)
        users = ClientUser.objects.filter(client_id=client_id)
        messages.success(request, 'Users fetched successfully.')
    except Client.DoesNotExist:
        messages.error(request, 'Client does not exist.')
        return redirect(request.META.get('HTTP_REFERER', 'default_if_referer_not_found'))
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', 'default_if_referer_not_found'))

    return render(request, "clients/users_clientadmin.html", {"users": users, "client": client})


class ClientUserCreateView(View):
    def get(self, request, *args, **kwargs):
        # Get the client from the logged in user
        client = request.user.client

        # Create a new form
        form = ClientUserForm(client=client)
        
        # Render the template with the form
        return render(request, 'clients/create_clientuser_and_assign_scorm.html', {'form': form})
    
    def post(self, request, *args, **kwargs):        
        # Get the client from the logged in user
        client = request.user.client

        form = ClientUserForm(request.POST, client=client)
        if form.is_valid():
            # Create a new ClientUser
            client_user = ClientUser.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                learner_id=ClientUser.objects.count() + 1,  # Autoincrement learner_id
                client=client
            )
            client_user.save()
            
            # Generate the id
            encrypted_id = encrypt_data(client_user.client.id, form.cleaned_data['scorm'].scorm_id)

            # Define the URL
            url = request.build_absolute_uri(reverse('validate-and-launch'))  # Use Django's reverse function to generate the URL

            # Define the headers
            headers = {
                'Content-Type': 'application/json'
            }

            # Define the data
            data = {
                "id": encrypted_id,
                "referringurl": client_user.client.domains,
                "learner_id": str(client_user.learner_id),
                "name": f"{client_user.first_name} {client_user.last_name}"
            }

            # Make the POST request
            response = requests.post(url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                # Save the launch_url returned in the response to the ClientUser
                client_user.launch_url = response.json()['launch_url']
                client_user.cloudscorm_user_id = response.json()['cloudscorm_user_id']
                client_user.save()

                return JsonResponse({'message': 'Client user created successfully'}, status=201)
            else:
                return JsonResponse({'error': 'Failed to create client user'}, status=400)
        else:
            return JsonResponse({'error': form.errors}, status=400)