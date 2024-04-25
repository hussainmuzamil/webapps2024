from django.contrib.auth import authenticate, logout, login
from rest_framework_simplejwt.tokens import RefreshToken

from django.shortcuts import render, redirect

from payapp.models import AmountRequest, Transaction
from .forms import UserRegistrationForm, AdminRegistrationForm, LoginForm

from .models import Principal

from django.contrib.auth.decorators import login_required
from payapp.models import Account


def signup(request):
    if request.method == 'POST':
        try:
            user_form = UserRegistrationForm(request.POST)
            if user_form.is_valid():
                user = user_form.save()
                if user is not None:
                    return render(request, "create_account.html", {'user': user})
                else:
                    authenticate(email=user_form.email, password=user_form.password)
                    print(request.user)
                    return render(request, "create_account.html", {'user': user})
            else:
                print(user_form.errors)
                return render(request, "error.html", {"error_message": str(user_form.errors)})
        except Exception as e:
            print(e)
            return render(request, "error.html", {"error_message": str(e)})
    else:
        form = UserRegistrationForm()
        return render(request, "auth/signup.html", {'form': form})


def user_balance(request):
    account = Account.objects.filter(user=request.user).first()
    return account.amount, account.currency


@login_required
def home(request):
    user = request.user
    if user.is_staff:
        template_name = 'transactions.html'
        nav_items = [
            {'label': 'Home', 'url': '/register/home/'},
            {'label': 'Users', 'url': '/register/users/'},
            {'label': 'Add User', 'url': '/register/add-users/'},
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
                'amount': transaction.amount,
                'date': transaction.transaction_date
            })
        return render(request, template_name, {'nav_items': nav_items, 'transactions': transactions_data})
    else:
        balance, currency = user_balance(request)
        template_name = 'requests.html'
        nav_items = [
            {'label': 'Home', 'url': '/register/home/'},
            {'label': "Transactions History", 'url': '/payapp/transactions/'},
            {'label': 'Transfer Amount', 'url': '/payapp/send-amount/'},
            {'label': 'Request Amount', 'url': '/payapp/request-amount/'},
            {'label': 'Logout', 'url': '/register/logout/'}
        ]
        amount_requests = AmountRequest.objects.filter(receiver=request.user).select_related('requester', 'receiver')
        return render(request, template_name, {'nav_items': nav_items, 'requests': amount_requests,
                                               'balance': balance, 'currency': currency})


@login_required
def add_users(request):
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
    user = request.user
    if user.is_staff:
        if request.method == 'POST':
            try:
                user_form = AdminRegistrationForm(request.POST)
                if user_form.is_valid():
                    user = user_form.save()
                    if user is not None:
                        return redirect("home")
                else:
                    print(user_form.errors)
                    return render(request, "error.html", {"error_message": str(user_form.errors)})
            except Exception as e:
                print(e)
                return render(request, "error.html", {"error_message": str(e)})
        else:
            form = AdminRegistrationForm()
            return render(request, "auth/register.html", {'form': form, 'nav_items': nav_items})
    return render(request, "error.html", {"error_message": str("authentication is required")})


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.is_active:  # Check if the user account is active
                    login(request, user)
                    return redirect('home')
                else:
                    return render(request, "error.html", {"error_message": "Your account is disabled."})
            else:
                return render(request, "error.html", {"error_message": "Invalid email or password."})
        else:
            return render(request, "error.html", {"error_message": "Invalid form data."})
    elif request.user.is_authenticated:
        return redirect('home')
    else:
        form = LoginForm()
        return render(request, "auth/login.html", {'form': form})


def logout_view(request):
    logout(request)
    return redirect("authenticate_user")


@login_required
def get_all_user(request):
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
    users = Principal.objects.filter(is_admin=False)
    return render(request, "auth/users.html", {'users': users, 'nav_items': nav_items})
