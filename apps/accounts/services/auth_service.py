import logging

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.constants import AuthMessages
from apps.core.utils.exceptions import (
    InternalServerErrorException,
    NotAuthenticatedException,
    UnauthorizedAccessException,
)
from apps.accounts.models import Role, User, UserRole


logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def register(validated_data: dict) -> dict:
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        logger.info("User created during registration", extra={"user_id": str(user.id)})

        try:
            viewer_role = Role.objects.get(name=Role.VIEWER)
        except Role.DoesNotExist as exc:
            logger.exception("Viewer role missing during registration")
            raise InternalServerErrorException(AuthMessages.ROLE_SEED_MISSING) from exc

        UserRole.objects.create(user=user, role=viewer_role)
        logger.info("Default role assigned to user", extra={"user_id": str(user.id), "role": Role.VIEWER})

        tokens = AuthService._generate_tokens(user)
        return {"user": user, "tokens": tokens}

    @staticmethod
    def login(email: str, password: str) -> dict:
        user = authenticate(username=email, password=password)

        if user is None:
            logger.warning("Login failed due to invalid credentials", extra={"email": email})
            raise NotAuthenticatedException(AuthMessages.INVALID_CREDENTIALS)

        if not user.is_active:
            logger.warning("Login attempted for inactive account", extra={"user_id": str(user.id)})
            raise UnauthorizedAccessException(AuthMessages.ACCOUNT_INACTIVE)

        tokens = AuthService._generate_tokens(user)
        logger.info("Login successful", extra={"user_id": str(user.id)})
        return {"user": user, "tokens": tokens}

    @staticmethod
    def _generate_tokens(user: User) -> dict:
        refresh = RefreshToken.for_user(user)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}
