from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_run.views import get_company_details, RunViewSet, UserViewSet

router = DefaultRouter()
router.register("runs", RunViewSet, basename="runs")
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("company_details/", get_company_details, name="get_company_details"),
    path("", include(router.urls)),
]
