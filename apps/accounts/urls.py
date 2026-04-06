from django.urls import path

from apps.accounts.views import (
    LoginView,
    RegisterView,
    RoleListView,
    UserDetailView,
    UserListView,
)

app_name = "accounts"

urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="auth-register"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("users", UserListView.as_view(), name="user-list"),
    path("users/<uuid:pk>", UserDetailView.as_view(), name="user-detail"),
    path("roles", RoleListView.as_view(), name="role-list"),
]
