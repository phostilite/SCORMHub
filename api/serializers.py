from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from clients.models import Client, ClientUser

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ClientUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUser
        fields = '__all__'

class ValidateAndLaunchRequest(serializers.Serializer):
    id = serializers.CharField(help_text="Encrypted ID containing client ID and SCORM ID.")
    referringurl = serializers.URLField(help_text="The referring domain of the learner.")
    learner_id = serializers.CharField(help_text="The unique learner identifier.")
    name = serializers.CharField(help_text="The first name of the learner.")

class ValidateAndLaunchResponse(serializers.Serializer):
    launch_url = serializers.URLField(help_text="The URL to launch the SCORM package.", required=False)
    error = serializers.CharField(help_text="An error message if validation or launch URL generation fails.", required=False)