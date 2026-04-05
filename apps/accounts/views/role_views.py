import logging

from drf_spectacular.utils import extend_schema
from apps.core.utils.swagger_helpers import roles_schema
from rest_framework.views import APIView

from apps.accounts.constants import RoleMessages
from apps.accounts.models import Role
from apps.accounts.permissions import IsActiveUser, IsAdmin
from apps.accounts.serializers import RoleSerializer
from apps.core.utils.api_response import APIResponse
from apps.core.utils.swagger_helpers import create_response_serializer


logger = logging.getLogger(__name__)


RoleListResponseSerializer = create_response_serializer(RoleSerializer, many=True, name_prefix='RoleList')


@roles_schema
class RoleListView(APIView):
    permission_classes = [IsAdmin, IsActiveUser]

    @extend_schema(responses={200: RoleListResponseSerializer})
    def get(self, request):
        roles = Role.objects.all()
        logger.debug("Roles list requested", extra={"count": roles.count()})
        return APIResponse.success(
            message=RoleMessages.ROLES_FETCHED,
            data=RoleSerializer(roles, many=True).data,
        )
