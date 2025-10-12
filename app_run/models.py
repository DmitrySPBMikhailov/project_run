from django.db import models
from django.contrib.auth.models import User


class StatusChoices(models.TextChoices):
    """
    Every run instance can have 3 types of status
    """

    INIT = "init"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Run(models.Model):
    """
    A model for storing running results of the athletes
    """

    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=11, choices=StatusChoices.choices, default=StatusChoices.INIT
    )
    distance = models.FloatField(null=True, blank=True)
    run_time_seconds = models.IntegerField(null=True)
    speed = models.FloatField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.athlete.username} {self.created_at.strftime("%d-%m-%Y %H:%M:%S")}"
        )


class AthleteInfo(models.Model):
    """
    One to one model to User
    Allows to add additional information
    """

    user_id = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="athlete_profile",
    )
    goals = models.TextField(blank=True, default="")
    weight = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user_id}"


class Challenge(models.Model):
    """
    Created after 10 runs
    """

    athlete = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=32, default="Сделай 10 Забегов!")

    def __str__(self):
        return f"{self.athlete}"


class Position(models.Model):
    """
    Latitude and longitude of the athlete during run
    """

    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    date_time = models.DateTimeField(null=True, auto_now_add=False)
    speed = models.FloatField(
        null=True,
        blank=True,
    )
    distance = models.FloatField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.run}"


class CollectibleItem(models.Model):
    """
    Items for athletes to be chased
    """

    name = models.CharField(max_length=128)
    uid = models.CharField(max_length=128)
    latitude = models.FloatField()
    longitude = models.FloatField()
    picture = models.URLField(max_length=512)
    value = models.IntegerField()
    users = models.ManyToManyField(User, related_name="items", null=True, blank=True)

    def __str__(self):
        return self.name


class Subscribe(models.Model):
    """
    Athelete can subscribe on coach.
    """

    coach = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="coach",
    )
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name="athlete")
    rating = models.SmallIntegerField(null=True, blank=True)

    def __str__(self):
        return str(f"{self.athlete.last_name} подписан на ${self.coach.last_name}")
