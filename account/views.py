from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from .permissions import UserByTokenPermission
from rest_framework import response, status
from .serializer import AccountSerializer
from rest_framework import exceptions
from django.conf import settings
from .models import Account
import requests
import json


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
            f"{settings.AUTHORIZATION_URL}{instance.id}/", headers=headers)
        if r.status_code != 204:
            raise exceptions.APIException
        instance.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer: AccountSerializer = self.get_serializer(
            data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        r = requests.post(settings.AUTHORIZATION_URL, data=request.data)
        if r.status_code != 201:
            return response.Response(data=r.json(), status=r.status_code)
        new_user = r.json()
        instance: Account = serializer.save_with_id(**new_user)
        serializer: AccountSerializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return response.Response({**new_user, **serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
