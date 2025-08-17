from django.urls import path

from app_run.views import get_company_details

urlpatterns = [
    path("company_details/", get_company_details, name="get_company_details"),
]
