import pytest

from apps.accounts.models import Role, User


REGISTER_URL = "/api/v1/accounts/auth/register"
LOGIN_URL = "/api/v1/accounts/auth/login"
USERS_URL = "/api/v1/accounts/users"


@pytest.mark.django_db
class TestRegistration:
	def test_register_success_returns_201_with_tokens(self, api_client):
		payload = {
			"email": "newuser@test.com",
			"password": "securepass123",
			"first_name": "Test",
			"last_name": "User",
		}
		response = api_client.post(REGISTER_URL, payload, format="json")

		assert response.status_code == 201
		assert response.data["status"] is True
		assert "tokens" in response.data["data"]
		assert "access" in response.data["data"]["tokens"]
		assert "refresh" in response.data["data"]["tokens"]

	def test_register_auto_assigns_viewer_role_when_user_created(self, api_client):
		payload = {
			"email": "viewer@test.com",
			"password": "securepass123",
		}
		api_client.post(REGISTER_URL, payload, format="json")
		user = User.objects.get(email="viewer@test.com")

		assert user.role_name == Role.VIEWER

	def test_register_duplicate_email_returns_400_when_email_exists(self, api_client, viewer_user):
		payload = {
			"email": viewer_user.email,
			"password": "securepass123",
		}
		response = api_client.post(REGISTER_URL, payload, format="json")

		assert response.status_code == 400
		assert response.data["status"] is False

	def test_register_short_password_returns_400_when_password_too_short(self, api_client):
		payload = {
			"email": "shortpass@test.com",
			"password": "123",
		}
		response = api_client.post(REGISTER_URL, payload, format="json")

		assert response.status_code == 400
		assert response.data["status"] is False

	def test_register_missing_email_returns_400_when_email_not_provided(self, api_client):
		response = api_client.post(REGISTER_URL, {"password": "securepass123"}, format="json")

		assert response.status_code == 400
		assert response.data["status"] is False


@pytest.mark.django_db
class TestLogin:
	def test_login_valid_credentials_returns_tokens_when_user_is_active(self, api_client, viewer_user):
		response = api_client.post(
			LOGIN_URL,
			{"email": viewer_user.email, "password": "testpass123"},
			format="json",
		)

		assert response.status_code == 200
		assert response.data["status"] is True
		assert "tokens" in response.data["data"]

	def test_login_wrong_password_returns_401_when_password_invalid(self, api_client, viewer_user):
		response = api_client.post(
			LOGIN_URL,
			{"email": viewer_user.email, "password": "wrongpassword"},
			format="json",
		)

		assert response.status_code == 401
		assert response.data["status"] is False

	def test_login_inactive_user_returns_403_when_account_deactivated(self, api_client, viewer_user):
		viewer_user.is_active = False
		viewer_user.save(update_fields=["is_active", "updated_at"])

		response = api_client.post(
			LOGIN_URL,
			{"email": viewer_user.email, "password": "testpass123"},
			format="json",
		)

		assert response.status_code == 403
		assert response.data["status"] is False

	def test_login_nonexistent_email_returns_401_when_user_not_found(self, api_client):
		response = api_client.post(
			LOGIN_URL,
			{"email": "nobody@test.com", "password": "testpass123"},
			format="json",
		)

		assert response.status_code == 401
		assert response.data["status"] is False


@pytest.mark.django_db
class TestUserManagement:
	def test_list_users_admin_returns_200_when_role_is_admin(self, admin_client):
		response = admin_client.get(USERS_URL)

		assert response.status_code == 200
		assert response.data["status"] is True

	def test_list_users_viewer_returns_403_when_role_is_viewer(self, viewer_client):
		response = viewer_client.get(USERS_URL)

		assert response.status_code == 403
		assert response.data["status"] == "error"

	def test_list_users_analyst_returns_403_when_role_is_analyst(self, analyst_client):
		response = analyst_client.get(USERS_URL)

		assert response.status_code == 403
		assert response.data["status"] == "error"

	def test_update_user_role_admin_succeeds_when_role_payload_valid(self, admin_client, viewer_user):
		url = f"/api/v1/accounts/users/{viewer_user.id}"
		response = admin_client.patch(url, {"role": Role.ANALYST}, format="json")

		assert response.status_code == 200
		assert response.data["status"] is True
		assert response.data["data"]["role"] == Role.ANALYST

	def test_admin_cannot_deactivate_themselves_when_setting_inactive_false(self, admin_client, admin_user):
		url = f"/api/v1/accounts/users/{admin_user.id}"
		response = admin_client.patch(url, {"is_active": False}, format="json")

		assert response.status_code == 400
		assert response.data["status"] is False

	def test_update_user_viewer_returns_403_when_non_admin_attempts_patch(self, viewer_client, viewer_user):
		url = f"/api/v1/accounts/users/{viewer_user.id}"
		response = viewer_client.patch(url, {"role": Role.ADMIN}, format="json")

		assert response.status_code == 403
		assert response.data["status"] == "error"
