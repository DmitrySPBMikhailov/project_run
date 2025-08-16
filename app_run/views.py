from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings


@api_view(["GET"])
def get_company_details(request):
    """
    Sends main information about the company.
    """
    return Response(settings.COMPANY_INFORMATION)
