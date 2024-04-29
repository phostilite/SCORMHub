from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_core_admin = models.BooleanField(default=False) 
    is_client_admin = models.BooleanField(default=False)
