import logging

from apps.core.utils.swagger_helpers import RECORD_FILTER_PARAMS, records_schema
from drf_spectacular.utils import extend_schema
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
from apps.records.throttling import RecordsReadThrottle, RecordsWriteThrottle
from apps.core.utils.swagger_helpers import create_paginated_response_serializer, create_response_serializer


logger = logging.getLogger(__name__)


RecordListResponseSerializer = create_paginated_response_serializer(RecordSerializer, name_prefix='RecordList')
RecordDetailResponseSerializer = create_response_serializer(RecordSerializer, name_prefix='RecordDetail')


@extend_schema(tags=['records'], parameters=RECORD_FILTER_PARAMS)
class RecordListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        if self.request.method == 'POST':
            return [RecordsWriteThrottle()]
        return [RecordsReadThrottle()]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsViewerOrAbove()]

    @extend_schema(responses={200: RecordListResponseSerializer})
    def get(self, request):
        queryset = RecordService.get_records(request.query_params)
        page = paginate_queryset(queryset, request, serializer_class=RecordSerializer)
        return APIResponse.success(
            message='Records retrieved successfully.',
            data=page,
        )

    @extend_schema(request=RecordCreateSerializer, responses={201: RecordDetailResponseSerializer})
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


@records_schema
class RecordDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        if self.request.method == 'GET':
            return [RecordsReadThrottle()]
        return [RecordsWriteThrottle()]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsViewerOrAbove()]
        return [IsAdmin()]

    @extend_schema(responses={200: RecordDetailResponseSerializer})
    def get(self, request, pk):
        record = RecordService.get_record_by_id(pk)
        return APIResponse.success(
            message='Record retrieved successfully.',
            data=RecordSerializer(record).data,
        )

    @extend_schema(request=RecordUpdateSerializer, responses={200: RecordDetailResponseSerializer})
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

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        RecordService.delete_record(pk)
        return APIResponse.success(
            message='Record deleted successfully.',
            data=None,
            status_code=204,
        )
