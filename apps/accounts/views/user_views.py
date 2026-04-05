import logging

from rest_framework.views import APIView

from apps.accounts.constants import AuthErrorCodes, CommonMessages, UserMessages
from apps.accounts.permissions import IsActiveUser, IsAdmin
from apps.accounts.serializers import UserSerializer, UserUpdateSerializer
from apps.accounts.services import UserService
from apps.core.utils.api_response import APIResponse
from apps.core.utils.pagination import paginate_queryset
from apps.core.utils.exceptions import InvalidInputException, ResourceNotFoundException


logger = logging.getLogger(__name__)


class UserListView(APIView):
    permission_classes = [IsAdmin, IsActiveUser]

    def get(self, request):
        filters = {
            "role": request.query_params.get("role"),
            "is_active": request.query_params.get("is_active"),
        }
        queryset = UserService.get_all_users(filters)
        page = paginate_queryset(queryset, request, serializer_class=UserSerializer)

        return APIResponse.success(message=UserMessages.USERS_FETCHED, data=page)


class UserDetailView(APIView):
    permission_classes = [IsAdmin, IsActiveUser]

    def get(self, request, pk):
        try:
            user = UserService.get_user_by_id(pk)
        except ResourceNotFoundException as exc:
            logger.warning("User detail lookup failed", extra={"user_id": str(pk)})
            return APIResponse.error(
                message=str(exc),
                status_code=404,
            )

        return APIResponse.success(message=UserMessages.USER_FETCHED, data=UserSerializer(user).data)

    def patch(self, request, pk):
        serializer = UserUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            logger.warning("User update validation failed", extra={"user_id": str(pk), "errors": serializer.errors})
            return APIResponse.error(
                message=CommonMessages.VALIDATION_ERROR,
                data=serializer.errors,
                status_code=400,
            )

        try:
            user = UserService.update_user(
                requesting_admin=request.user,
                target_user_id=pk,
                validated_data=serializer.validated_data,
            )
        except InvalidInputException as exc:
            logger.warning("User update blocked", extra={"user_id": str(pk), "reason": str(exc)})
            return APIResponse.error(
                message=str(exc),
                error_code=AuthErrorCodes.CANNOT_DEACTIVATE_SELF,
                status_code=400,
            )
        except ResourceNotFoundException as exc:
            logger.warning("User update failed due to missing resource", extra={"user_id": str(pk), "reason": str(exc)})
            return APIResponse.error(
                message=str(exc),
                status_code=404,
            )

        return APIResponse.success(message=UserMessages.USER_UPDATED, data=UserSerializer(user).data)
