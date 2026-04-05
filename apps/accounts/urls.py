from django.urls import path

from apps.accounts.views import (
    LoginView,
    RegisterView,
    RoleListView,
    UserDetailView,
    UserListView,
)

urlpatterns = [
    path("v1/register/", RegisterView.as_view(), name="register"),
    path("v1/login/", LoginView.as_view(), name="login"),
    path("v1/users/", UserListView.as_view(), name="user-list"),
    path("v1/users/<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("v1/roles/", RoleListView.as_view(), name="role-list"),
]
