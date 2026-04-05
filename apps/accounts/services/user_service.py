import logging

from apps.accounts.constants import UserMessages
from apps.accounts.models import Role, User, UserRole
from apps.core.utils.exceptions import InvalidInputException, ResourceNotFoundException


logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def get_all_users(filters: dict):
        queryset = User.objects.all().select_related("user_role__role")

        role = filters.get("role")
        if role:
            queryset = queryset.filter(user_role__role__name=role)

        is_active = filters.get("is_active")
        if is_active is not None and is_active != "":
            active_bool = str(is_active).lower() == "true"
            queryset = queryset.filter(is_active=active_bool)

        logger.debug("User list queried", extra={"filters": filters})
        return queryset

    @staticmethod
    def get_user_by_id(user_id: str) -> User:
        try:
            return User.objects.select_related("user_role__role").get(id=user_id)
        except User.DoesNotExist as exc:
            logger.warning("User not found", extra={"user_id": str(user_id)})
            raise ResourceNotFoundException(UserMessages.USER_NOT_FOUND) from exc

    @staticmethod
    def update_user(requesting_admin: User, target_user_id: str, validated_data: dict) -> User:
        user = UserService.get_user_by_id(target_user_id)

        if (
            "is_active" in validated_data
            and validated_data["is_active"] is False
            and str(user.id) == str(requesting_admin.id)
        ):
            logger.warning("Self-deactivation blocked", extra={"user_id": str(requesting_admin.id)})
            raise InvalidInputException(UserMessages.CANNOT_DEACTIVATE_SELF)

        if "is_active" in validated_data:
            user.is_active = validated_data["is_active"]
            user.save(update_fields=["is_active", "updated_at"])
            logger.info("User active state updated", extra={"user_id": str(user.id), "is_active": user.is_active})

        if "role" in validated_data:
            try:
                new_role = Role.objects.get(name=validated_data["role"])
            except Role.DoesNotExist as exc:
                logger.warning("Role not found for user update", extra={"role": validated_data.get("role")})
                raise ResourceNotFoundException(UserMessages.ROLE_NOT_FOUND) from exc

            UserRole.objects.update_or_create(user=user, defaults={"role": new_role})
            logger.info("User role updated", extra={"user_id": str(user.id), "role": new_role.name})

        user.refresh_from_db()
        return user
