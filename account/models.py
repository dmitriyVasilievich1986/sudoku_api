from django.db import models


class Account(models.Model):
    username = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
