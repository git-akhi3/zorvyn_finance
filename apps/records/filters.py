import logging

import django_filters
from django.db.models import Q

from apps.records.models import FinancialRecord


logger = logging.getLogger(__name__)


class FinancialRecordFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(field_name='type', lookup_expr='exact')
    category = django_filters.CharFilter(field_name='category', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    currency = django_filters.CharFilter(field_name='currency', lookup_expr='exact')
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    created_by = django_filters.UUIDFilter(field_name='created_by__id', lookup_expr='exact')
    search = django_filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        logger.debug('Record search query: %s', value)
        return queryset.filter(
            Q(category__icontains=value)
            | Q(notes__icontains=value)
            | Q(reference_number__icontains=value)
        )

    class Meta:
        model = FinancialRecord
        fields = [
            'type',
            'category',
            'status',
            'currency',
            'date_from',
            'date_to',
            'created_by',
            'search',
        ]
