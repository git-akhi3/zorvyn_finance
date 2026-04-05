import logging

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from apps.accounts.permissions import IsAnalystOrAbove
from apps.core.utils.api_response import APIResponse
from apps.core.utils.swagger_helpers import dashboard_schema
from apps.records.serializers.dashboard_serializers import (
    CategoryBreakdownSerializer,
    SummarySerializer,
    TrendsSerializer,
)
from apps.records.serializers.record_serializers import RecordSerializer
from apps.records.services import DashboardService
from apps.core.utils.swagger_helpers import create_response_serializer
from apps.records.throttling import DashboardReadThrottle


logger = logging.getLogger(__name__)


SummaryResponseSerializer = create_response_serializer(SummarySerializer, name_prefix='DashboardSummary')
TrendsResponseSerializer = create_response_serializer(TrendsSerializer, name_prefix='DashboardTrends')
CategoryResponseSerializer = create_response_serializer(CategoryBreakdownSerializer, name_prefix='DashboardCategory')
ActivityResponseSerializer = create_response_serializer(RecordSerializer, many=True, name_prefix='DashboardActivity')


@dashboard_schema
class DashboardSummaryView(APIView):
    permission_classes = [IsAnalystOrAbove]
    throttle_classes = [DashboardReadThrottle]

    @extend_schema(responses={200: SummaryResponseSerializer})
    def get(self, request):
        data = DashboardService.get_summary()
        serializer = SummarySerializer(data)
        return APIResponse.success(
            message='Dashboard summary retrieved successfully.',
            data=serializer.data,
        )


@dashboard_schema
class DashboardTrendsView(APIView):
    permission_classes = [IsAnalystOrAbove]
    throttle_classes = [DashboardReadThrottle]

    @extend_schema(responses={200: TrendsResponseSerializer})
    def get(self, request):
        data = DashboardService.get_trends()
        serializer = TrendsSerializer(data)
        return APIResponse.success(
            message='Dashboard trends retrieved successfully.',
            data=serializer.data,
        )


@dashboard_schema
class DashboardCategoriesView(APIView):
    permission_classes = [IsAnalystOrAbove]
    throttle_classes = [DashboardReadThrottle]

    @extend_schema(responses={200: CategoryResponseSerializer})
    def get(self, request):
        data = DashboardService.get_category_breakdown()
        serializer = CategoryBreakdownSerializer(data)
        return APIResponse.success(
            message='Category breakdown retrieved successfully.',
            data=serializer.data,
        )


@dashboard_schema
class DashboardActivityView(APIView):
    permission_classes = [IsAnalystOrAbove]
    throttle_classes = [DashboardReadThrottle]

    @extend_schema(responses={200: ActivityResponseSerializer})
    def get(self, request):
        records = DashboardService.get_recent_activity(limit=10)
        return APIResponse.success(
            message='Recent activity retrieved successfully.',
            data=RecordSerializer(records, many=True).data,
        )
