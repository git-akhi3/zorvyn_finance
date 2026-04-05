from apps.accounts.views.auth_views import LoginView, RegisterView
from apps.accounts.views.role_views import RoleListView
from apps.accounts.views.user_views import UserDetailView, UserListView

__all__ = [
	"RegisterView",
	"LoginView",
	"UserListView",
	"UserDetailView",
	"RoleListView",
]
