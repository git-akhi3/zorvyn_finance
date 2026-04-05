import logging
from datetime import timedelta
from decimal import Decimal

from django.db.models import Q, Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.utils.timezone import now

from apps.records.constants import RecordType
from apps.records.models import FinancialRecord


logger = logging.getLogger(__name__)


class DashboardService:
    @staticmethod
    def get_summary() -> dict:
        logger.debug('Fetching dashboard summary')

        today = now().date()
        current_month_start = today.replace(day=1)
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        base_qs = FinancialRecord.objects.all()

        totals = base_qs.aggregate(
            total_income=Sum('amount', filter=Q(type=RecordType.INCOME)),
            total_expense=Sum('amount', filter=Q(type=RecordType.EXPENSE)),
        )

        total_income = totals['total_income'] or Decimal('0')
        total_expense = totals['total_expense'] or Decimal('0')
        net_balance = total_income - total_expense

        current = base_qs.filter(date__gte=current_month_start).aggregate(
            income=Sum('amount', filter=Q(type=RecordType.INCOME)),
            expense=Sum('amount', filter=Q(type=RecordType.EXPENSE)),
        )

        last = base_qs.filter(
            date__gte=last_month_start,
            date__lte=last_month_end,
        ).aggregate(
            income=Sum('amount', filter=Q(type=RecordType.INCOME)),
            expense=Sum('amount', filter=Q(type=RecordType.EXPENSE)),
        )

        current_income = current['income'] or Decimal('0')
        current_expense = current['expense'] or Decimal('0')
        last_income = last['income'] or Decimal('0')
        last_expense = last['expense'] or Decimal('0')

        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': net_balance,
            'period_comparison': {
                'current_month': {
                    'income': current_income,
                    'expense': current_expense,
                },
                'last_month': {
                    'income': last_income,
                    'expense': last_expense,
                },
                'income_change': DashboardService.safe_pct_change(current_income, last_income),
                'expense_change': DashboardService.safe_pct_change(current_expense, last_expense),
            },
        }

    @staticmethod
    def safe_pct_change(current_val: Decimal, previous_val: Decimal) -> str:
        if not previous_val:
            return 'N/A'
        change = ((current_val - previous_val) / previous_val) * 100
        return f'{change:+.1f}%'

    @staticmethod
    def get_trends() -> dict:
        logger.debug('Fetching dashboard trends')

        today = now().date()
        twelve_months_ago = today.replace(day=1) - timedelta(days=365)

        monthly = (
            FinancialRecord.objects.filter(date__gte=twelve_months_ago)
            .annotate(month=TruncMonth('date'))
            .values('month', 'type')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        daily = (
            FinancialRecord.objects.filter(date__year=today.year, date__month=today.month)
            .annotate(day=TruncDay('date'))
            .values('day', 'type')
            .annotate(total=Sum('amount'))
            .order_by('day')
        )

        return {
            'monthly': DashboardService.reshape_trends(monthly, 'month'),
            'daily': DashboardService.reshape_trends(daily, 'day'),
        }

    @staticmethod
    def reshape_trends(qs, date_key: str) -> list:
        grouped = {}
        for row in qs:
            key = row[date_key]
            if key not in grouped:
                grouped[key] = {
                    date_key: key,
                    RecordType.INCOME: Decimal('0'),
                    RecordType.EXPENSE: Decimal('0'),
                }
            grouped[key][row['type']] = row['total'] or Decimal('0')
        return list(grouped.values())

    @staticmethod
    def get_category_breakdown() -> dict:
        logger.debug('Fetching category breakdown')

        results = {}

        for record_type in [RecordType.INCOME, RecordType.EXPENSE]:
            rows = (
                FinancialRecord.objects.filter(type=record_type)
                .values('category')
                .annotate(total=Sum('amount'))
                .order_by('-total')
            )

            type_total = sum((row['total'] for row in rows if row['total']), Decimal('0'))

            breakdown = []
            for row in rows:
                amount = row['total'] or Decimal('0')
                percentage = (
                    Decimal(str(round((amount / type_total) * 100, 1)))
                    if type_total
                    else Decimal('0')
                )
                breakdown.append(
                    {
                        'category': row['category'],
                        'total': amount,
                        'percentage': percentage,
                    }
                )

            results[record_type] = breakdown

        return results

    @staticmethod
    def get_recent_activity(limit: int = 10):
        logger.debug('Fetching recent activity, limit=%s', limit)

        return FinancialRecord.objects.select_related('created_by').order_by('-created_at')[:limit]
