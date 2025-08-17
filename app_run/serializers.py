from rest_framework import serializers
from .models import Run


class RunSerializer(serializers.ModelSerializer):
    """
    Serializer for Run Model
    """

    class Meta:
        model = Run
        fields = "__all__"
