from django.urls import path

from apps.accounts.views import (
    LoginView,
    MeView,
    RegisterView,
    RoleListView,
    UserDetailView,
    UserListView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("roles/", RoleListView.as_view(), name="role-list"),
]
