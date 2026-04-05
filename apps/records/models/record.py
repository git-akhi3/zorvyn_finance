import logging

from django.db import models

from apps.core.models.base import BaseModel
from apps.records.constants import RecordStatus, RecordType


logger = logging.getLogger(__name__)


class FinancialRecord(BaseModel):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=RecordType.CHOICES)
    category = models.CharField(max_length=100)
    date = models.DateField()
    notes = models.TextField(blank=True, default='')
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(
        max_length=15,
        choices=RecordStatus.CHOICES,
        default=RecordStatus.COMPLETED,
    )
    reference_number = models.CharField(max_length=30, unique=True, editable=False)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='financial_records',
    )

    class Meta(BaseModel.Meta):
        db_table = 'financial_records'
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['type']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['created_by']),
            models.Index(fields=['reference_number']),
        ]

    def __str__(self):
        return f'{self.reference_number} | {self.type} | {self.amount}'
