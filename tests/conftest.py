import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Role
from apps.records.constants import RecordStatus
from tests.factories import FinancialRecordFactory, RoleFactory, UserFactory, UserRoleFactory


@pytest.fixture(autouse=True)
def seed_roles(db):
    RoleFactory(name=Role.VIEWER, description="Viewer role")
    RoleFactory(name=Role.ANALYST, description="Analyst role")
    RoleFactory(name=Role.ADMIN, description="Admin role")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def viewer_user(db):
    user = UserFactory()
    role = RoleFactory(name=Role.VIEWER)
    UserRoleFactory(user=user, role=role)
    return user


@pytest.fixture
def analyst_user(db):
    user = UserFactory()
    role = RoleFactory(name=Role.ANALYST)
    UserRoleFactory(user=user, role=role)
    return user


@pytest.fixture
def admin_user(db):
    user = UserFactory()
    role = RoleFactory(name=Role.ADMIN)
    UserRoleFactory(user=user, role=role)
    return user


@pytest.fixture
def viewer_client(api_client, viewer_user):
    token = RefreshToken.for_user(viewer_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.fixture
def analyst_client(api_client, analyst_user):
    token = RefreshToken.for_user(analyst_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    token = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.fixture
def pending_record(db, admin_user):
    return FinancialRecordFactory(created_by=admin_user, status=RecordStatus.PENDING)


@pytest.fixture
def completed_record(db, admin_user):
    return FinancialRecordFactory(created_by=admin_user, status=RecordStatus.COMPLETED)
