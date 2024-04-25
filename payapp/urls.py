from django.urls import path, include
from .views import *

urlpatterns = [
    path('requests/', get_all_request_amount, name="amount_requests"),
    path('send-amount/', send_amount, name="send_amount"),
    path('request-amount/', request_amount, name="request_amount"),
    path('request_action/', request_action, name="request_action"),
    path("transactions/", get_transactions_by_user, name="transactions"),
    path("users-transactions/", transactions, name="users_transactions"),
    path("create-account/", amount, name="create_account"),
    path('conversion/<str:currency1>/<str:currency2>/<str:amount>/',
         GetCurrencyConversion.as_view(),
         name='currency_conversion'),

]