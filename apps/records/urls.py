from django.urls import path

from apps.records.views import RecordDetailView, RecordListCreateView
from apps.records.views.dashboard_views import DashboardSummaryView, DashboardTrendsView, DashboardCategoriesView, DashboardActivityView

app_name = "records"

urlpatterns = [
    path('transactions', RecordListCreateView.as_view(), name='transaction-list-create'),
    path('transactions/<uuid:pk>', RecordDetailView.as_view(), name='transaction-detail'),
    path('dashboard/summary', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/trends', DashboardTrendsView.as_view(), name='dashboard-trends'),
    path('dashboard/categories', DashboardCategoriesView.as_view(), name='dashboard-categories'),
    path('dashboard/activity', DashboardActivityView.as_view(), name='dashboard-activity'),
]
