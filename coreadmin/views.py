from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from .forms import AdminLoginForm


def admin_login_view(request):
    """
    View function for handling the admin login.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    if request.user.is_authenticated and request.user.is_core_admin:
        return redirect("scorm-dashboard")
    
    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_core_admin:
                    login(request, user)
                    return redirect("scorm-dashboard")
                else:
                    messages.error(
                        request, "This account doesn't have admin permissions."
                    )
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AdminLoginForm()
    return render(request, "coreadmin/login.html", {"form": form})


def admin_logout_view(request):
    """
    Logs out the admin user and redirects to the admin login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: A redirect response to the admin login page.
    """
    logout(request)
    return redirect("admin-login")
