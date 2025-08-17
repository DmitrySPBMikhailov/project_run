from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from rest_framework import viewsets
from .models import Run
from .serializers import RunSerializer, UserSerializer
from django.contrib.auth.models import User
from django.db.models import CharField, Value


@api_view(["GET"])
def get_company_details(request):
    """
    Sends main information about the company.
    """
    return Response(settings.COMPANY_INFORMATION)


class RunViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing run instances.
    """

    queryset = Run.objects.all()
    serializer_class = RunSerializer


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
    """

    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer

    def get_queryset(self):
        param_type = self.request.query_params.get("type")
        if param_type == "coach":
            queryset = self.queryset.filter(is_staff=True)
        elif param_type == "athlete":
            queryset = self.queryset.filter(is_staff=False)
        else:
            queryset = self.queryset
        return queryset
