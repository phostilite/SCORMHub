from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="SCORM Validation and Launch API",
        default_version="v1",
        description="This API validates a learner's access to a SCORM package, creates a user on CloudScorm if necessary, and returns a launch URL. It accepts encrypted data containing the client and SCORM IDs, along with learner information such as learner ID and name. If the data is valid, it generates a launch URL for the SCORM package. The API handles various error scenarios such as missing data, invalid client or referring domain, and failed URL generation.",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path(
        "validate-and-launch/",
        views.validate_and_launch,
        name="validate-and-launch",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path('get_scorm_data/<int:client_id>/<int:scorm_id>/', views.get_scorm_data, name='get_scorm_data'),
    path('sync_courses/', views.sync_courses, name='sync_courses'),
    path('user_scorm_status/', views.user_scorm_status, name='user_scorm_status'),
]
