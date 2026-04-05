import logging
import random
import string
from datetime import datetime

from django.utils import timezone

from apps.core.utils.exceptions import (
    InternalServerErrorException,
    InvalidInputException,
    ResourceNotFoundException,
)
from apps.records.constants import RecordStatus
from apps.records.filters import FinancialRecordFilter
from apps.records.models import FinancialRecord


logger = logging.getLogger(__name__)


class RecordService:
    @staticmethod
    def generate_reference_number() -> str:
        date_part = datetime.now().strftime('%Y%m%d')

        for _ in range(5):
            ref = f"TXN-{date_part}-" + ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=4)
            )

            if not FinancialRecord.all_objects.filter(reference_number=ref).exists():
                return ref

        logger.error("Failed to generate unique reference number after 5 attempts")
        raise InternalServerErrorException(
            "Could not generate a unique reference number. Please retry."
        )

    @staticmethod
    def create_record(validated_data: dict, created_by) -> FinancialRecord:
        logger.info('Creating financial record for user %s', created_by.id)
        reference_number = RecordService.generate_reference_number()
        return FinancialRecord.objects.create(
            **validated_data,
            reference_number=reference_number,
            created_by=created_by,
        )

    @staticmethod
    def get_records(query_params: dict):
        queryset = FinancialRecord.objects.select_related('created_by').all()
        filtered = FinancialRecordFilter(query_params, queryset=queryset)
        return filtered.qs

    @staticmethod
    def get_record_by_id(record_id: str) -> FinancialRecord:
        try:
            return FinancialRecord.objects.select_related('created_by').get(id=record_id)
        except FinancialRecord.DoesNotExist:
            raise ResourceNotFoundException('Financial record not found.')

    @staticmethod
    def update_record(record_id: str, validated_data: dict) -> FinancialRecord:
        record = RecordService.get_record_by_id(record_id)

        if record.status in [RecordStatus.COMPLETED, RecordStatus.CANCELLED]:
            raise InvalidInputException(
                'Completed or cancelled records cannot be modified.'
            )

        logger.info('Updating financial record %s', record_id)

        for field, value in validated_data.items():
            setattr(record, field, value)

        update_fields = list(validated_data.keys()) + ['updated_at']
        record.save(update_fields=update_fields)
        record.refresh_from_db()
        return record

    @staticmethod
    def delete_record(record_id: str) -> None:
        record = RecordService.get_record_by_id(record_id)
        record.is_deleted = True
        record.deleted_at = timezone.now()
        record.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
        logger.info('Soft deleted financial record %s', record_id)
