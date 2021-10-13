from rest_framework import permissions, exceptions
from django.conf import settings
import requests


class UserByTokenPermission(permissions.BasePermission):
    def has_permission(self, request, view, *args, **kwargs) -> dict:
        if request.method == "POST":
            return True
        token: str = request.META.get("HTTP_AUTHORIZATION", "")
        if token is None or token == "":
            raise exceptions.NotAuthenticated
        headers: dict = {"Authorization": token}
        r: requests.Response = requests.get(
            settings.AUTHORIZATION_URL, headers=headers)
        if r.status_code != 200:
            raise exceptions.NotAuthenticated
        user: dict = r.json()
        request.user = user
        return True
