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
    PositionViewSet,
    CollectibleItemViewSet,
    upload_collectible_items,
)

router = DefaultRouter()
router.register("runs", RunViewSet, basename="runs")
router.register("users", UserViewSet, basename="users")
router.register("challenges", ChallengesViewSet, basename="challenges")
router.register("positions", PositionViewSet, basename="positions")
router.register("collectible_item", CollectibleItemViewSet, basename="collectible")

urlpatterns = [
    path("company_details/", get_company_details, name="get_company_details"),
    path("runs/<int:id>/start/", StartRunView.as_view(), name="start_run"),
    path("runs/<int:id>/stop/", StopRunView.as_view(), name="stop_run"),
    path("athlete_info/<int:id>/", AthleteInfoView.as_view(), name="athlete_info"),
    path("upload_file/", upload_collectible_items, name="upload_file"),
    path("", include(router.urls)),
]
