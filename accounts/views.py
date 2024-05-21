from django.shortcuts import render

def landing_page_view(request):
    """
    View function for the landing page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    return render(request, "accounts/index.html")

def about_page_view(request):
    """
    View function for the about page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    return render(request, "accounts/about.html")

def contact_page_view(request):
    """
    View function for the contact page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    return render(request, "accounts/contact.html")

