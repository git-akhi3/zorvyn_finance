import logging

from rest_framework.views import APIView

from apps.accounts.permissions import IsAnalystOrAbove
from apps.core.utils.api_response import APIResponse
from apps.records.serializers.dashboard_serializers import (
    CategoryBreakdownSerializer,
    SummarySerializer,
    TrendsSerializer,
)
from apps.records.serializers.record_serializers import RecordSerializer
from apps.records.services import DashboardService


logger = logging.getLogger(__name__)


class DashboardSummaryView(APIView):
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        data = DashboardService.get_summary()
        serializer = SummarySerializer(data)
        return APIResponse.success(
            message='Dashboard summary retrieved successfully.',
            data=serializer.data,
        )


class DashboardTrendsView(APIView):
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        data = DashboardService.get_trends()
        serializer = TrendsSerializer(data)
        return APIResponse.success(
            message='Dashboard trends retrieved successfully.',
            data=serializer.data,
        )


class DashboardCategoriesView(APIView):
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        data = DashboardService.get_category_breakdown()
        serializer = CategoryBreakdownSerializer(data)
        return APIResponse.success(
            message='Category breakdown retrieved successfully.',
            data=serializer.data,
        )


class DashboardActivityView(APIView):
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        records = DashboardService.get_recent_activity(limit=10)
        return APIResponse.success(
            message='Recent activity retrieved successfully.',
            data=RecordSerializer(records, many=True).data,
        )
