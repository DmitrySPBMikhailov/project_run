from django.db import models
from django.contrib.auth.models import User


class Run(models.Model):
    """
    A model for storing running results of the athletes
    """

    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, default="")

    def __str__(self):
        return (
            f"{self.athlete.username} {self.created_at.strftime("%d-%m-%Y %H:%M:%S")}"
        )
