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
