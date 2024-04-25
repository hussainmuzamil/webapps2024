from rest_framework import serializers
from .models import Transaction, Account, AmountRequest


class GetAllTransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "sender_account", "receiver_account", "amount"]


class AmountRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmountRequest
        fields = ["id", "requester", "receiver", "amount"]


class AmountRequestActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmountRequest
        fields = ["id", "status"]


class CreateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["amount", "currency"]
