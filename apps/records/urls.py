from django.urls import path

from apps.records.views import RecordDetailView, RecordListCreateView
from apps.records.views.dashboard_views import DashboardSummaryView, DashboardTrendsView, DashboardCategoriesView, DashboardActivityView

urlpatterns = [
    path('v1/transaction-create', RecordListCreateView.as_view(), name='record-list-create'),
    path('v1/transaction/<uuid:pk>', RecordDetailView.as_view(), name='record-detail'),
    path('v1/dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('v1/dashboard/trends/', DashboardTrendsView.as_view(), name='dashboard-trends'),
    path('v1/dashboard/categories/', DashboardCategoriesView.as_view(), name='dashboard-categories'),
    path('v1/dashboard/activity/', DashboardActivityView.as_view(), name='dashboard-activity'),
]
