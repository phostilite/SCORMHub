from django.contrib import admin
from .models import Client, ClientUser, UserScormStatus

admin.site.register(Client)
admin.site.register(ClientUser)
admin.site.register(UserScormStatus)