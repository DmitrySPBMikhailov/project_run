from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_run.views import (
    get_company_details,
    RunViewSet,
    UserViewSet,
    StartRunView,
    StopRunView,
)

router = DefaultRouter()
router.register("runs", RunViewSet, basename="runs")
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("company_details/", get_company_details, name="get_company_details"),
    path("runs/<int:id>/start/", StartRunView.as_view(), name="start_run"),
    path("runs/<int:id>/stop/", StopRunView.as_view(), name="stop_run"),
    path("", include(router.urls)),
]
