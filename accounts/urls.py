from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.landing_page_view, name='landing-page'),
    path('about/', views.about_page_view, name='about-page'),
    path('contact/', views.contact_page_view, name='contact-page')
]
