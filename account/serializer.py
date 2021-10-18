from .models import Account
from rest_framework.serializers import ModelSerializer
from rest_framework import exceptions


class AccountSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"

    def save_with_id(self, id, *args, **kwargs):
        instance: Account = Account.create(**self.validated_data)
        instance.id = id
        instance.save()
        return instance
