from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from rest_framework import viewsets
from .models import Run
from .serializers import RunSerializer


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
