"""
Reusable drf-spectacular decorators and shared schema helpers.
"""

from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema


auth_schema = extend_schema(tags=['auth'])
users_schema = extend_schema(tags=['users'])
roles_schema = extend_schema(tags=['roles'])
records_schema = extend_schema(tags=['records'])
dashboard_schema = extend_schema(tags=['dashboard'])


RECORD_FILTER_PARAMS = [
    OpenApiParameter('type', OpenApiTypes.STR, description='Filter by type: income or expense'),
    OpenApiParameter('category', OpenApiTypes.STR, description='Filter by category (case-insensitive)'),
    OpenApiParameter('status', OpenApiTypes.STR, description='Filter by status: pending, completed, cancelled'),
    OpenApiParameter('date_from', OpenApiTypes.DATE, description='Filter records from this date (YYYY-MM-DD)'),
    OpenApiParameter('date_to', OpenApiTypes.DATE, description='Filter records up to this date (YYYY-MM-DD)'),
    OpenApiParameter('search', OpenApiTypes.STR, description='Search category, notes, reference number'),
    OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by: date, amount, created_at (prefix - for desc)'),
    OpenApiParameter('page', OpenApiTypes.INT, description='Page number for pagination'),
]


def create_response_serializer(data_serializer_class=None, *, many=False, name_prefix='Api'):
    class_name = f'{name_prefix}ResponseSerializer'
    attrs = {
        'message': serializers.CharField(default='success'),
        'status': serializers.BooleanField(default=True),
    }
    if data_serializer_class is None:
        attrs['data'] = serializers.JSONField(required=False, allow_null=True)
    else:
        attrs['data'] = data_serializer_class(many=many)
    return type(class_name, (serializers.Serializer,), attrs)


def create_paginated_response_serializer(item_serializer_class, *, name_prefix='ApiList'):
    page_class_name = f'{name_prefix}PageDataSerializer'
    page_attrs = {
        'page': serializers.IntegerField(),
        'page_size': serializers.IntegerField(),
        'total_pages': serializers.IntegerField(),
        'total_items': serializers.IntegerField(),
        'next': serializers.CharField(allow_null=True, required=False),
        'previous': serializers.CharField(allow_null=True, required=False),
        'results': item_serializer_class(many=True),
    }
    page_serializer = type(page_class_name, (serializers.Serializer,), page_attrs)
    return create_response_serializer(page_serializer, name_prefix=name_prefix)
