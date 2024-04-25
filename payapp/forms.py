from django import forms
from django.core.exceptions import ValidationError

from .models import Account, AmountRequest


class AccountForm(forms.ModelForm):
    currency = forms.CharField(max_length=3)

    class Meta:
        model = Account
        fields = ['currency']


class RequestAmountForm(forms.Form):
    receiver_email = forms.EmailField()
    amount = forms.DecimalField(min_value=0)


class SendAmountForm(forms.Form):
    receiver_email = forms.EmailField()
    amount = forms.DecimalField(min_value=0)


class TransferActionForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput)
    receiver_email = forms.EmailField()
    amount = forms.DecimalField()


class AmountRequestActionForm(forms.Form):
    id = forms.IntegerField()
    status = forms.ChoiceField(choices=AmountRequest.REQUEST_STATUS)

    def clean_id(self):
        id = self.cleaned_data['id']
        try:
            amount_request = AmountRequest.objects.get(id=id)
        except AmountRequest.DoesNotExist:
            raise ValidationError('Invalid amount request ID')
        return amount_request

    def save(self):
        amount_request = self.cleaned_data['id']
        amount_request.status = self.cleaned_data['status']
        amount_request.save()

        return amount_request
