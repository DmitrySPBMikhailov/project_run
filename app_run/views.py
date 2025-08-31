from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import (
    Run,
    StatusChoices,
    AthleteInfo,
    Challenge,
    Position,
    CollectibleItem,
)
from .serializers import (
    RunSerializer,
    UserSerializer,
    ChallengesSerializer,
    PositionSerializer,
    CollectibleItemSerializer,
)
from django.contrib.auth.models import User
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Sum
from geopy.distance import geodesic
from openpyxl import load_workbook


@api_view(["GET"])
def get_company_details(request):
    """
    Sends main information about the company.
    """
    return Response(settings.COMPANY_INFORMATION)


class AppPagination(PageNumberPagination):
    page_size_query_param = "size"
    max_page_size = 50


class RunViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing run instances.
    There is also additional fetch for User Model via select_related through
    athlete field.
    """

    queryset = Run.objects.select_related("athlete").all()
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "athlete"]
    ordering_fields = ["created_at"]
    ordering = ["id"]
    pagination_class = AppPagination


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset is for read only. It allows to see users.
    It accepts Query Parameters:
    ?type=coach
    ?type=athlete
    ?type=*
    Coach returns users when is_staff property is True
    Athlete returns users where is_staff is False
    if another argument is provided viewSet returns both
    The viewSet does not show superusers.

    Additionally viewSet allows to search users by first_name
    or last_name.
    """

    queryset = User.objects.exclude(is_superuser=True).annotate(
        runs_finished_count=Count("run", filter=Q(run__status=StatusChoices.FINISHED))
    )
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["first_name", "last_name"]
    ordering = ["id"]
    ordering_fields = ["date_joined"]
    pagination_class = AppPagination

    def get_queryset(self):
        param_type = self.request.query_params.get("type")
        if param_type == "coach":
            queryset = self.queryset.filter(is_staff=True)
        elif param_type == "athlete":
            queryset = self.queryset.filter(is_staff=False)
        else:
            queryset = self.queryset
        return queryset


class StartRunView(APIView):
    """
    Change status for Run instance to IN_PROGRESS
    Will return 404 if no object found
    Will raise 400 bad request if run status if IN_PROGRESS or FINISHED
    """

    def post(self, request, id):
        run = get_object_or_404(Run, id=id)
        if (
            run.status == StatusChoices.IN_PROGRESS
            or run.status == StatusChoices.FINISHED
        ):
            data = {"status": "bad_request"}
            return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
        run.status = StatusChoices.IN_PROGRESS
        run.save()
        data = {"status": "success"}
        return JsonResponse(data, status=status.HTTP_200_OK)


class StopRunView(APIView):
    """
    Change status for Run instance to FINISHED
    Will return 404 if no object found
    Will raise 400 bad request if run instance has not been started.
    If two positions are related to current run it will calculate distance
    """

    challenge_name_10_runs = "Сделай 10 Забегов!"
    challenge_name_50_km = "Пробеги 50 километров!"

    def post(self, request, id):
        run = get_object_or_404(Run, id=id)
        if run.status == StatusChoices.INIT or run.status == StatusChoices.FINISHED:
            data = {"status": "bad_request"}
            return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
        run.status = StatusChoices.FINISHED
        positions = Position.objects.filter(run=run)
        length = len(positions)
        total = 0
        if length > 1:
            for index, position in enumerate(positions):
                if index == length - 1:
                    break
                start = (positions[index].latitude, positions[index].longitude)
                finish = (positions[index + 1].latitude, positions[index + 1].longitude)
                total += geodesic(start, finish).km
            run.distance = round(total, 3)
        run.save()
        user = User.objects.get(id=run.athlete.id)
        if not self.has_challenge(
            user, self.challenge_name_10_runs
        ) and self.has_ten_runs(user):
            Challenge.objects.create(
                athlete=user, full_name=self.challenge_name_10_runs
            )
        self.calculate_total_distance(user)
        data = {"status": "success"}
        return JsonResponse(data, status=status.HTTP_200_OK)

    def has_ten_runs(self, user):
        runs_count = Run.objects.filter(
            athlete=user, status=StatusChoices.FINISHED
        ).count()
        return runs_count >= 10

    def has_challenge(self, user, challenge_name):
        return Challenge.objects.filter(athlete=user, full_name=challenge_name).exists()

    def calculate_total_distance(self, user):
        total_distance = Run.objects.filter(athlete=user).aggregate(Sum("distance"))
        if (
            not self.has_challenge(user, self.challenge_name_50_km)
            and total_distance["distance__sum"]
            and total_distance["distance__sum"] >= 50
        ):
            Challenge.objects.create(athlete=user, full_name=self.challenge_name_50_km)
        return


class AthleteInfoView(APIView):
    """
    GET or PUT request to see additional info about athlete
    If AthleteInfo does not exist django will create it.
    """

    def get(self, request, id):
        athlete, _ = AthleteInfo.objects.select_related("user_id").get_or_create(
            user_id_id=id
        )
        data = {
            "goals": athlete.goals,
            "weight": athlete.weight,
            "user_id": athlete.user_id.id,
        }
        return JsonResponse(data, status=status.HTTP_200_OK)

    def put(self, request, id):
        goals = request.data.get("goals")
        weight = request.data.get("weight")

        if not goals or not weight:
            return JsonResponse(
                {"detail": "Please provide goals and weight"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            weight = int(weight)
            assert 0 < weight < 900
        except (ValueError, AssertionError):
            return JsonResponse(
                {"detail": "weight should be greater than 0 and smaller than 900"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        athlete, _ = AthleteInfo.objects.update_or_create(
            user_id_id=id,
            defaults={"goals": goals, "weight": weight},
        )

        return JsonResponse(
            {"goals": athlete.goals, "weight": athlete.weight, "user_id": id},
            status=status.HTTP_201_CREATED,
        )


class ChallengesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Shows all challenges by athletes
    If params provided /?athlete=<id> this endpoint retrieves challenges by a particular athlete
    """

    serializer_class = ChallengesSerializer

    def get_queryset(self):
        queryset = Challenge.objects.all()
        athlete_id = self.request.query_params.get("athlete")
        if athlete_id:
            queryset = queryset.filter(athlete_id=athlete_id)
        return queryset


class PositionViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing position instances.
    There is validation in the serializer
    """

    queryset = Position.objects.select_related("run").all()
    serializer_class = PositionSerializer

    def get_queryset(self):
        param_type = self.request.query_params.get("run")
        try:
            param_type = int(param_type)
        except:
            param_type = ""

        if param_type:
            queryset = self.queryset.filter(run=param_type)
        else:
            queryset = self.queryset
        return queryset


class CollectibleItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Shows all Collectible Items
    """

    serializer_class = CollectibleItemSerializer
    queryset = CollectibleItem.objects.all()


@api_view(["POST"])
def upload_collectible_items(request):
    """
    Allows to upload data from xlsx format
    """
    file = request.FILES.get("file")
    if not file:
        data = {"error": "Please provide xlsx file"}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
    # Проверка и чтение файла
    workbook = load_workbook(filename=file, data_only=True)
    sheet = workbook.active

    # Headers of the file
    headers = [
        "name",
        "uid",
        "value",
        "latitude",
        "longitude",
        "picture",
    ]

    errors = []

    for _, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        # row is tuple now => make it dict
        item_data = dict(zip(headers, row))

        serializer = CollectibleItemSerializer(data=item_data)
        if serializer.is_valid():
            serializer.save()
        else:
            # [] for errors inside this row
            error_colums = []
            for field in serializer.errors.keys():
                error_colums.append(item_data[field])
            errors.append(error_colums)

    return JsonResponse(errors, status=status.HTTP_200_OK, safe=False)
