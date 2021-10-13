from django.db import models
from rest_framework import exceptions


class Account(models.Model):
    username = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls: models.Model, username: str = None, *args: tuple, **kwargs: dict) -> models.Model:
        if username is None or not isinstance(username, str):
            raise exceptions.ValidationError(
                {"username": "The field cannot be empty"})
        if cls.objects.filter(username=username).count() > 0:
            raise exceptions.ValidationError(
                {"username": "This username is already in use"})
        return cls(username=username)
