from rest_framework import serializers
from .models import Run, Challenge, Position, StatusChoices, CollectibleItem
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
    runs_finished = serializers.IntegerField(
        source="runs_finished_count", read_only=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "date_joined",
            "username",
            "last_name",
            "first_name",
            "type",
            "runs_finished",
        ]

    def get_type(self, obj):
        return "coach" if obj.is_staff else "athlete"


class ChallengesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ["full_name", "athlete"]


class PositionSerializer(serializers.ModelSerializer):
    """
    Position model serializer
    Additional validation for run status, and valid latitude and longitude
    """

    class Meta:
        model = Position
        fields = ["run", "latitude", "longitude", "id"]

    def validate_run(self, value):
        if value.status != StatusChoices.IN_PROGRESS:
            raise serializers.ValidationError(
                f"Статус забега должен быть {StatusChoices.IN_PROGRESS}"
            )
        return value

    def validate_latitude(self, value):
        if not -90.0 <= value <= 90.0:
            raise serializers.ValidationError(
                f"Широта должна находиться в диапазоне [-90.0, 90.0] градусов."
            )
        if self.count_decimal_digits(value) > 4:
            raise serializers.ValidationError(
                f"Широта может иметь до 4 знаков после запятой."
            )
        return value

    def validate_longitude(self, value):
        if not -180.0 <= value <= 180.0:
            raise serializers.ValidationError(
                f" Долгота должна находиться в диапазоне [-180.0, 180.0] градусов."
            )
        if self.count_decimal_digits(value) > 4:
            raise serializers.ValidationError(
                f"Долгота может иметь до 4 знаков после запятой."
            )
        return value

    def count_decimal_digits(self, number):
        s = str(number)
        if "." in s:
            return len(s) - s.find(".") - 1
        else:
            return 0


class CollectibleItemSerializer(serializers.ModelSerializer):
    """
    Serializer for Collectible Item
    """

    class Meta:
        model = CollectibleItem
        fields = [
            "name",
            "uid",
            "value",
            "latitude",
            "longitude",
            "picture",
        ]
