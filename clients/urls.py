from django.urls import path, include

from . import views

urlpatterns = [
    path('login/', views.client_login_view, name='client-login'),
    path('logout/', views.client_logout_view, name='client-logout'),
    path('client-details/<int:client_id>/', views.client_details_view_for_clientadmin, name='client-details-clientadmin'),
    path('client-details/<int:client_id>/users/', views.users_list_for_clientadmin, name='users-list-for-clientadmin')
]
