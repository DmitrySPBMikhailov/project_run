from rest_framework import serializers
from .models import Run
from django.contrib.auth.models import User


class RunSerializer(serializers.ModelSerializer):
    """
    Serializer for Run Model
    """

    class Meta:
        model = Run
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User Model
    Custom Field is added based on is_staff property
    Field type is added.
    If user is_staff then type == coach
    Else athlete
    """

    type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "date_joined",
            "username",
            "last_name",
            "first_name",
            "type",
        ]

    def get_type(self, obj):
        return "coach" if obj.is_staff else "athlete"
