from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Run, StatusChoices
from .serializers import RunSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q


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
    """

    def post(self, request, id):
        run = get_object_or_404(Run, id=id)
        if run.status == StatusChoices.INIT or run.status == StatusChoices.FINISHED:
            data = {"status": "bad_request"}
            return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
        run.status = StatusChoices.FINISHED
        run.save()
        data = {"message": "This is a successful response.", "status": "success"}
        return JsonResponse(data, status=status.HTTP_200_OK)
