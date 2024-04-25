from django.urls import path, include
from register.views import *

urlpatterns = [
    path("add-users/", add_users, name="add_users"),
    path("auth/user/signup", signup, name="register_user"),
    path("login", login_view, name="authenticate_user"),
    path("logout/", logout_view, name="logout"),
    path("home/", home, name="home"),
    path("users/", get_all_user, name="users")
]