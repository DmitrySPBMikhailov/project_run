from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_run.views import (
    get_company_details,
    RunViewSet,
    UserViewSet,
    StartRunView,
    StopRunView,
    AthleteInfoView,
    ChallengesViewSet,
)

router = DefaultRouter()
router.register("runs", RunViewSet, basename="runs")
router.register("users", UserViewSet, basename="users")
router.register("challenges", ChallengesViewSet, basename="challenges")

urlpatterns = [
    path("company_details/", get_company_details, name="get_company_details"),
    path("runs/<int:id>/start/", StartRunView.as_view(), name="start_run"),
    path("runs/<int:id>/stop/", StopRunView.as_view(), name="stop_run"),
    path("athlete_info/<int:id>/", AthleteInfoView.as_view(), name="athlete_info"),
    path("", include(router.urls)),
]
