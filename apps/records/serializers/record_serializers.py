import logging
from decimal import Decimal

from rest_framework import serializers

from apps.core.utils.exceptions import InvalidAmountException
from apps.records.constants import RecordStatus, RecordType
from apps.records.models import FinancialRecord


logger = logging.getLogger(__name__)


class RecordCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )
    type = serializers.ChoiceField(choices=RecordType.CHOICES)
    category = serializers.CharField(max_length=100)
    date = serializers.DateField()
    notes = serializers.CharField(required=False, default='')
    currency = serializers.CharField(max_length=10, default='INR')
    status = serializers.ChoiceField(
        choices=RecordStatus.CHOICES,
        required=False,
        default=RecordStatus.COMPLETED,
    )

    def validate_amount(self, value):
        if value <= 0:
            raise InvalidAmountException('Amount must be greater than zero.')
        return value


class RecordUpdateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        required=False,
    )
    category = serializers.CharField(max_length=100, required=False)
    date = serializers.DateField(required=False)
    notes = serializers.CharField(required=False)
    currency = serializers.CharField(max_length=10, required=False)
    status = serializers.ChoiceField(choices=RecordStatus.CHOICES, required=False)

    def validate_amount(self, value):
        if value <= 0:
            raise InvalidAmountException('Amount must be greater than zero.')
        return value


class RecordSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = FinancialRecord
        fields = [
            'id',
            'reference_number',
            'amount',
            'type',
            'category',
            'date',
            'notes',
            'currency',
            'status',
            'created_by',
            'created_at',
            'updated_at',
        ]

    def get_created_by(self, obj):
        return {
            'id': str(obj.created_by.id),
            'email': obj.created_by.email,
        }
