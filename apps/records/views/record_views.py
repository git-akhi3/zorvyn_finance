import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsViewerOrAbove
from apps.core.utils.api_response import APIResponse
from apps.core.utils.exceptions import ValidationException
from apps.core.utils.pagination import paginate_queryset
from apps.records.serializers import (
    RecordCreateSerializer,
    RecordSerializer,
    RecordUpdateSerializer,
)
from apps.records.services import RecordService


logger = logging.getLogger(__name__)


class RecordListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsViewerOrAbove()]

    def get(self, request):
        queryset = RecordService.get_records(request.query_params)
        page = paginate_queryset(queryset, request, serializer_class=RecordSerializer)
        return APIResponse.success(
            message='Records retrieved successfully.',
            data=page,
        )

    def post(self, request):
        serializer = RecordCreateSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationException(serializer.errors)

        record = RecordService.create_record(
            validated_data=serializer.validated_data,
            created_by=request.user,
        )
        return APIResponse.success(
            message='Financial record created successfully.',
            data=RecordSerializer(record).data,
            status_code=201,
        )


class RecordDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsViewerOrAbove()]
        return [IsAdmin()]

    def get(self, request, pk):
        record = RecordService.get_record_by_id(pk)
        return APIResponse.success(
            message='Record retrieved successfully.',
            data=RecordSerializer(record).data,
        )

    def patch(self, request, pk):
        serializer = RecordUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationException(serializer.errors)

        record = RecordService.update_record(
            record_id=pk,
            validated_data=serializer.validated_data,
        )
        return APIResponse.success(
            message='Record updated successfully.',
            data=RecordSerializer(record).data,
        )

    def delete(self, request, pk):
        RecordService.delete_record(pk)
        return APIResponse.success(
            message='Record deleted successfully.',
            data=None,
            status_code=204,
        )
