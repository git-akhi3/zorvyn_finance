import logging

from rest_framework.views import APIView

from apps.accounts.constants import RoleMessages
from apps.accounts.models import Role
from apps.accounts.permissions import IsActiveUser, IsAdmin
from apps.accounts.serializers import RoleSerializer
from apps.core.utils.api_response import APIResponse


logger = logging.getLogger(__name__)


class RoleListView(APIView):
    permission_classes = [IsAdmin, IsActiveUser]

    def get(self, request):
        roles = Role.objects.all()
        logger.debug("Roles list requested", extra={"count": roles.count()})
        return APIResponse.success(
            message=RoleMessages.ROLES_FETCHED,
            data=RoleSerializer(roles, many=True).data,
        )
