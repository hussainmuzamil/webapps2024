from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, logout, login
from django.urls import reverse
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Transaction, Account, AmountRequest
from register.models import Principal
from .forms import AccountForm, SendAmountForm, RequestAmountForm, AmountRequestActionForm
import requests


def user_balance(request):
    account = Account.objects.filter(user=request.user).first()
    if account is not None:
        print(request.user)
        print(account.amount)
    return account.amount, account.currency


@login_required
def get_transactions_by_user(request):
    user = request.user
    balance, currency = user_balance(request)
    print(balance)
    nav_items = [
        {'label': 'Home', 'url': '/register/home/'},
        {'label': "Transactions History", 'url': '/payapp/transactions/'},
        {'label': 'Transfer Amount', 'url': '/payapp/send-amount/'},
        {'label': 'Request Amount', 'url': '/payapp/request-amount/'},
        {'label': 'Logout', 'url': '/register/logout/'}
    ]
    if not user.is_staff:
        try:
            account = Account.objects.filter(user=user)
            user_transactions = (Transaction.objects.filter(sender_account__in=account) |
                                 Transaction.objects.filter(receiver_account__in=account))
            transactions_data = []
            for transaction in user_transactions:
                print(transaction.transaction_date)
                transactions_data.append({
                    'sender_email': transaction.sender_account.user.email,
                    'receiver_email': transaction.receiver_account.user.email,
                    'sender_amount': transaction.sender_amount,
                    'receiver_amount': transaction.receiver_amount,
                    'sender_currency': transaction.sender_currency,
                    'receiver_currency': transaction.receiver_currency,
                    'date': transaction.transaction_date
                })
            return render(request, "transactions.html", {'transactions': transactions_data, "nav_items": nav_items,
                                                         'balance': balance, 'currency': currency})
        except Exception as e:
            return render(request, "error.html", {'error_message': str(e)})
    else:
        return render(request, "error.html", {'error_message': "Permission Denied"})


@login_required
def send_amount(request):
    user = request.user
    balance, currency = user_balance(request)
    if user.is_staff:
        template_name = 'transactions.html'
        nav_items = [
            {'label': 'Home', 'url': '/register/home/'},
            {'label': 'Users', 'url': '/register/users/'},
            {'label': 'Add User', 'url': '/register/add-users/'},
            {'label': 'Logout', 'url': '/register/logout/'}
        ]
    else:
        template_name = 'requests.html'
        nav_items = [
            {'label': 'Home', 'url': '/register/home/'},
            {'label': "Transactions History", 'url': '/payapp/transactions/'},
            {'label': 'Transfer Amount', 'url': '/payapp/send-amount/'},
            {'label': 'Request Amount', 'url': '/payapp/request-amount/'},
            {'label': 'Logout', 'url': '/register/logout/'}
        ]
    if request.method == 'POST':
        user = request.user
        print(user)
        form = SendAmountForm(request.POST)
        if form.is_valid():
            sender_principal = request.user
            receiver_email = form.cleaned_data["receiver_email"]
            if user.email == receiver_email:
                return render(request, "error.html", {'error_message': "Receiver Email Should Be Different"})
            receiver_principal = Principal.objects.filter(email=receiver_email).first()
            if not receiver_principal:
                return render(request, "error.html", {'error_message': "No User exists"})
            try:
                sender_account = Account.objects.filter(user=sender_principal).first()
            except ObjectDoesNotExist:
                return render(request, "error.html", {'error_message': "Sender account does not exist"})
            try:
                receiver_account = Account.objects.filter(user=receiver_principal).first()
            except ObjectDoesNotExist:
                return render(request, "error.html", {'error_message': "Receiver account does not exist"})
            amount_to_send = form.cleaned_data['amount']

            if sender_account is None:
                return render(request, "error.html", {'error_message': "Sender account does not exist"})

            if receiver_account is None:
                return render(request, "error.html", {'error_message': 'Receiver Account does not exist'})

            # conversion/<str:currency1>/<str:currency2>/<str:amount>/
            if sender_account.currency != receiver_account.currency:
                conversion_endpoint = f'/payapp/conversion/{sender_account.currency}/{receiver_account.currency}/{amount_to_send}'
                conversion_url = request.build_absolute_uri(conversion_endpoint)
                response = requests.get(conversion_url)
                if response.status_code == 200:
                    conversion_data = response.json()
                    converted_amount = conversion_data['value']
                    print(converted_amount)
                    amount_to_send = converted_amount
                    print(amount_to_send)
                else:
                    error_message = 'Failed to get currency conversion rate'
                    return render(request, "error.html", {'error_message': error_message})
            if sender_account.amount < Decimal(amount_to_send):
                return render(request, "error.html", {'error_message': "Insufficient Balance"})

            # Convert amount_to_send to Decimal before performing subtraction
            amount_to_send_decimal = Decimal(amount_to_send)

            sender_account.amount -= Decimal(form.cleaned_data['amount'])
            sender_account.save()
            receiver_account.amount += amount_to_send_decimal
            receiver_account.save()
            transaction = Transaction.objects.create(
                sender_account=sender_account,
                receiver_account=receiver_account,
                receiver_amount=float(amount_to_send),
                sender_amount=float(form.cleaned_data['amount']),
                sender_currency=sender_account.currency,
                receiver_currency=receiver_account.currency,
            )
            transaction.is_active = True
            transaction.save()

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')
                else:
                    return render(request, "error.html", {"error_message": "Your account is disabled."})
        else:
            return render(request, "error.html", {'error_message': str(form.errors)})
    else:
        form = SendAmountForm()
        return render(request, "send_amount.html",
                      {'form': form, 'nav_items': nav_items, 'balance': balance, 'currency': currency})


def request_amount(request):
    user = request.user
    balance, currency = user_balance(request)
    if user.is_staff:
        template_name = 'transactions.html'
        nav_items = [
            {'label': 'Home', 'url': '/register/home/'},
            {'label': 'Users', 'url': '/register/users/'},
            {'label': 'Add User', 'url': '/register/add-users/'},
            {'label': 'Logout', 'url': '/register/logout/'}
        ]
    else:
        template_name = 'requests.html'
        nav_items = [
            {'label': 'Home', 'url': '/register/home/'},
            {'label': "Transactions History", 'url': '/payapp/transactions/'},
            {'label': 'Transfer Amount', 'url': '/payapp/send-amount/'},
            {'label': 'Request Amount', 'url': '/payapp/request-amount/'},
            {'label': 'Logout', 'url': '/register/logout/'}
        ]
    if request.method == 'POST':
        form = RequestAmountForm(request.POST)
        if form.is_valid():
            user = request.user
            receiver_email = form.cleaned_data.get("receiver_email")
            receiver = Principal.objects.filter(email=receiver_email).first()

            if not receiver:
                return render(request, "error.html", {'error_message': 'Invalid receiver email'})

            requested_amount = form.cleaned_data.get("amount")

            request = AmountRequest.objects.create(
                requester=user,
                receiver=receiver,
                amount=requested_amount
            )
            return redirect("home")  # Redirect to home page after successful request
        else:
            return render(request, "error.html", {'error_message': form.errors})
    else:
        form = RequestAmountForm()
        return render(request, "requests_amount.html", {'form': form, 'nav_items': nav_items,
                                                        'balance': balance, 'currency': currency})


@login_required
def request_action(request):
    print(request.user)
    if request.method == 'POST':
        form = AmountRequestActionForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect("home")
            except ValidationError as e:
                return render(request, "error.html", {'error_message': str(e)})
        else:
            return render(request, "error.html", {'error_message': str(form.errors)})
    else:
        return render(request, "error.html", {'error_message': str("can't process request")})


def get_all_request_amount(request):
    balance, currency = user_balance(request)
    amount_requests = AmountRequest.objects.filter(receiver=request.user)
    return render(request, "requests.html",
                  {'amount_requests': amount_requests, 'balance': balance, 'currency': currency})


def amount(request):
    if request.method == 'POST':
        form = AccountForm(data=request.POST)
        try:
            user_email = request.POST.get('email')
            user_password = request.POST.get('password')
            user = Principal.objects.filter(email__exact=user_email).first()
            login(request, user)
            print(user)
            nav_items = [
                {'label': 'Home', 'url': '/register/home/'},
                {'label': "Transactions History", 'url': '/payapp/transactions/'},
                {'label': 'Transfer Amount', 'url': '/payapp/send-amount/'},
                {'label': 'Request Amount', 'url': '/payapp/request-amount/'},
                {'label': 'Logout', 'url': '/register/logout/'}
            ]
            # print(request.user)
            if form.is_valid():
                selected_currency = form.cleaned_data.get("currency")
                account = Account.objects.create(
                    amount=1000,
                    currency=selected_currency,
                    user=user
                )
                account.is_active = True
                account.save()
                if user is not None:
                    print(user)
                    return render(request, "requests.html",
                                  {'user': user, 'nav_items': nav_items, })
                else:
                    return render(request, "requests.html", {'user': user, 'nav_items': nav_items})
            else:
                return render(request, "error.html", {'error_message': str(form.errors)})
        except Exception as e:
            return render(request, "error.html", {'error_message': str(e)})
    else:
        form = AccountForm()
        return render(request, "auth/signup.html", {'form': form})


class CombinedActionView(View):
    def post(self, request, *args, **kwargs):
        # Extract form data
        send_amount_form = SendAmountForm(request.POST)
        amount_request_action_form = AmountRequestActionForm(request.POST)

        if amount_request_action_form.is_valid():
            amount_request_action_form.save()

        if send_amount_form.is_valid():
            send_amount(request)

        return redirect("home")


class GetCurrencyConversion(APIView):
    def get(self, request, *args, **kwargs):
        currency1 = kwargs.get("currency1")
        currency2 = kwargs.get("currency2")
        amount_of_currency_1 = float(kwargs.get("amount"))
        print(currency1)
        print(currency2)
        print(amount_of_currency_1)
        rate = 0.0
        conversion_rates = {
            "GBP": {
                "USD": 1.42,
                "EUR": 1.17
            },
            "USD": {
                "GBP": 0.70,
                "EUR": 0.93
            },
            "EUR": {
                "GBP": 0.86,
                "USD": 1.07
            }
        }

        # Check if currencies are supported
        if currency1 not in conversion_rates or currency2 not in conversion_rates[currency1]:
            return Response({'error': 'Unsupported currencies'}, status=status.HTTP_400_BAD_REQUEST)

        conversion_rate = conversion_rates[currency1][currency2]
        converted_amount = amount_of_currency_1 * conversion_rate
        return Response({'msg': 'Currency Converted Successfully',
                         'value': converted_amount},
                        status=status.HTTP_200_OK)


@login_required
def transactions(request):
    # Retrieve all transactions
    balance, currency = user_balance(request)
    user = request.user
    if user.is_staff:
        template_name = 'transactions.html'
        nav_items = [
            {'label': 'Home', 'url': '/register/home/'},
            {'label': 'Users', 'url': '/register/users/'},
            {'label': 'Add User', 'url': '/register/add-users/'},
            {'label': 'Logout', 'url': '/register/logout/'}
        ]
    else:
        template_name = 'requests.html'
        nav_items = [
            {'label': 'Home', 'url': '/register/home/'},
            {'label': "Transactions History", 'url': '/payapp/transactions/'},
            {'label': 'Transfer Amount', 'url': '/payapp/send-amount/'},
            {'label': 'Request Amount', 'url': '/payapp/request-amount/'},
            {'label': 'Logout', 'url': '/register/logout/'}
        ]
    user_transactions = Transaction.objects.all()
    user_transactions = user_transactions.select_related('sender_account__user', 'receiver_account__user')

    transactions_data = []
    for transaction in user_transactions:
        print(transaction.transaction_date)
        transactions_data.append({
            'sender_email': transaction.sender_account.user.email,
            'receiver_email': transaction.receiver_account.user.email,
            'sender_amount': transaction.sender_amount,
            'receiver_amount': transaction.receiver_amount,
            'sender_currency': transaction.sender_currency,
            'receiver_currency': transaction.receiver_currency,
            'date': transaction.transaction_date
        })
    return render(request, "transactions.html", {'transactions': transactions_data, 'nav_items': nav_items})
