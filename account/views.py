from django.shortcuts import get_object_or_404
from .models import Account
from .serializer import AccountSerializer
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework import exceptions, serializers
from rest_framework.decorators import action
from rest_framework import permissions, response, status
import requests
from os import environ

AUTHORIZATION_URL = (
    environ.get("AUTHORIZATION_URL") or "http://localhost:3000/api/accounts/")


class UserByTokenPermission(permissions.BasePermission):
    def has_permission(self, request, view, *args, **kwargs) -> dict:
        if request.method == "POST":
            return True
        token: str = request.META.get("HTTP_AUTHORIZATION", "")
        if token is None or token == "":
            raise exceptions.NotAuthenticated
        headers: dict = {"Authorization": token}
        r: requests.Response = requests.get(AUTHORIZATION_URL, headers=headers)
        if r.status_code != 200:
            raise exceptions.NotAuthenticated
        user: dict = r.json()
        request.user = user
        return True


class AccountViewSet(ModelViewSet):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    permission_classes = [UserByTokenPermission]

    def list(self, request, *args, **kwargs):
        user = request.user
        instance = get_object_or_404(Account, id=user["id"])
        serializer = self.get_serializer(instance)
        return response.Response({**user, **serializer.data})

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if instance.id != user["id"]:
            raise exceptions.NotAuthenticated
        serializer = self.get_serializer(instance)
        return response.Response({**user, **serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user = request.user
        if instance.id != user["id"]:
            raise exceptions.NotAuthenticated
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return response.Response({**user, **serializer.data})

    def destroy(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if instance.id != user["id"]:
            raise exceptions.NotAuthenticated
        headers = {"Authorization": f"token {user['token']}"}
        r = requests.delete(
            f"{AUTHORIZATION_URL}{instance.id}/", headers=headers)
        if r.status_code != 204:
            raise exceptions.APIException
        instance.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        instance = Account.create(**request.data)
        r = requests.post(AUTHORIZATION_URL, data=request.data)
        if r.status_code != 201:
            return response.Response(data=r.json(), status=r.status_code)
        new_user = r.json()
        instance.id = new_user["id"]
        instance.save()
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return response.Response({**new_user, **serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
