from django.contrib import admin
from .models import Client, ClientUser

admin.site.register(Client)
admin.site.register(ClientUser)