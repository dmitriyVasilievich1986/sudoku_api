from django.shortcuts import get_object_or_404
from .models import Account
from .serializer import AccountSerializer
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework import exceptions, serializers
from rest_framework.decorators import action
from rest_framework import permissions, response
import requests
from os import environ

AUTHORIZATION_URL = (
    environ.get("AUTHORIZATION_URL") or "http://localhost:3000/api/accounts/")


def get_user_by_token(request) -> dict:
    token: str = request.META.get("HTTP_AUTHORIZATION", "")
    if token is None or token == "":
        raise exceptions.NotAuthenticated
    headers: dict = {"Authorization": token}
    r: requests.Response = requests.get(AUTHORIZATION_URL, headers=headers)
    if r.status_code != 200:
        raise exceptions.NotAuthenticated
    user: dict = r.json()
    return user


class AccountViewSet(ModelViewSet):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()

    def list(self, request, *args, **kwargs):
        user = get_user_by_token(request)
        instance = get_object_or_404(Account, id=user["id"])
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = get_user_by_token(request)
        instance = self.get_object()
        if instance.id != user["id"]:
            raise exceptions.NotAuthenticated
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)
