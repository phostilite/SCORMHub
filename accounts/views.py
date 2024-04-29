from django.shortcuts import render

def landing_page_view(request):
    """
    View function for the landing page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    return render(request, "accounts/landing_page.html")