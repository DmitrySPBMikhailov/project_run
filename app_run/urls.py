from django.urls import path

from .views import *

urlpatterns = [
    path("company_details/", get_company_details, name="get_company_details"),
]
