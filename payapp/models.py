from django.db import models
from register.models import Principal


# Create your models here.

class Account(models.Model):
    user = models.ForeignKey(Principal, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
    sender_account = models.ForeignKey(Account, related_name="sent_transaction", on_delete=models.CASCADE)
    receiver_account = models.ForeignKey(Account, related_name="received_transaction", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)


class AmountRequest(models.Model):
    REQUEST_STATUS = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    ]
    requester = models.ForeignKey(Principal, related_name='requests_sent', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Principal, related_name='requests_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)


class CurrencyRates(models.Model):
    currency1 = models.CharField(max_length=3)
    currency2 = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=10, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
