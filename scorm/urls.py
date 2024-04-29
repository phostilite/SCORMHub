from django.urls import path, include
from .views import get_all_scorms

urlpatterns = [
    path("get-all-scorms/", get_all_scorms, name="get-all-scorms"),
]
