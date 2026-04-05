from apps.records.views.record_views import RecordDetailView, RecordListCreateView
from apps.records.views.dashboard_views import (
    DashboardActivityView,
    DashboardCategoriesView,
    DashboardSummaryView,
    DashboardTrendsView,
)

__all__ = [
    'RecordListCreateView',
    'RecordDetailView',
    'DashboardSummaryView',
    'DashboardTrendsView',
    'DashboardCategoriesView',
    'DashboardActivityView',
]
