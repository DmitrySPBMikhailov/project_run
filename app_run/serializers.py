from rest_framework import serializers
from .models import Run, Challenge, Position, StatusChoices, CollectibleItem, Subscribe
from django.contrib.auth.models import User
from .utils import validate_latitude, validate_longitude


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


class CollectibleItemSerializer(serializers.ModelSerializer):
    """
    Serializer for Collectible Item
    """

    latitude = serializers.FloatField(validators=[validate_latitude])
    longitude = serializers.FloatField(validators=[validate_longitude])

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


class CollectibleItemSerializerExtended(CollectibleItemSerializer):

    class Meta(CollectibleItemSerializer.Meta):
        fields = CollectibleItemSerializer.Meta.fields + ["id"]


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


class UserSerializerExtended(UserSerializer):
    items = CollectibleItemSerializerExtended(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["items"]


class AthleteSerializerExtended(UserSerializerExtended):
    """For athlete — add field coach"""

    coach = serializers.SerializerMethodField()

    class Meta(UserSerializerExtended.Meta):
        fields = UserSerializerExtended.Meta.fields + ["coach"]

    def get_coach(self, obj):
        subscription = Subscribe.objects.filter(athlete=obj).first()
        return subscription.coach.id if subscription else None


class CoachSerializerExtended(UserSerializerExtended):
    """
    For coach - add list id of athletes
    """

    athletes = serializers.SerializerMethodField()

    class Meta(UserSerializerExtended.Meta):
        fields = UserSerializerExtended.Meta.fields + ["athletes"]

    def get_athletes(self, obj):
        return list(
            Subscribe.objects.filter(coach=obj).values_list("athlete_id", flat=True)
        )


class ChallengesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ["full_name", "athlete"]


class PositionSerializer(serializers.ModelSerializer):
    """
    Position model serializer
    Additional validation for run status, and valid latitude and longitude
    """

    latitude = serializers.FloatField(validators=[validate_latitude])
    longitude = serializers.FloatField(validators=[validate_longitude])
    date_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f")

    class Meta:
        model = Position
        fields = [
            "run",
            "latitude",
            "longitude",
            "id",
            "date_time",
            "speed",
            "distance",
        ]

    def validate_run(self, value):
        if value.status != StatusChoices.IN_PROGRESS:
            raise serializers.ValidationError(
                f"Статус забега должен быть {StatusChoices.IN_PROGRESS}"
            )
        return value


class AthleteChallengeSerializer(serializers.ModelSerializer):
    """
    Serializer for athelte data used as nested in ChallengesDisplay
    """

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class TotalChallengesSerializer(serializers.Serializer):
    name_to_display = serializers.CharField()
    athletes = AthleteChallengeSerializer(many=True)
