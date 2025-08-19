from rest_framework import serializers
from .models import Run
from django.contrib.auth.models import User


class AthleteSerializer(serializers.ModelSerializer):
    """
    Serializer for Athlete.
    This serializer is used as nested serializer in RunSerializer
    """

    class Meta:
        model = User
        fields = ["id", "username", "last_name", "first_name"]


class RunSerializer(serializers.ModelSerializer):
    """
    Serializer for Run Model
    There is nested serializer for UserModel
    """

    athlete_data = AthleteSerializer(source="athlete", read_only=True)

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
