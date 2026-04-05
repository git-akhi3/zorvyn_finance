from rest_framework import serializers


class PeriodSerializer(serializers.Serializer):
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense = serializers.DecimalField(max_digits=12, decimal_places=2)


class PeriodComparisonSerializer(serializers.Serializer):
    current_month = PeriodSerializer()
    last_month = PeriodSerializer()
    income_change = serializers.CharField()
    expense_change = serializers.CharField()


class SummarySerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    period_comparison = PeriodComparisonSerializer()


class MonthlyTrendEntrySerializer(serializers.Serializer):
    month = serializers.DateField()
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense = serializers.DecimalField(max_digits=12, decimal_places=2)


class DailyTrendEntrySerializer(serializers.Serializer):
    day = serializers.DateField()
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense = serializers.DecimalField(max_digits=12, decimal_places=2)


class TrendsSerializer(serializers.Serializer):
    monthly = MonthlyTrendEntrySerializer(many=True)
    daily = DailyTrendEntrySerializer(many=True)


class CategoryEntrySerializer(serializers.Serializer):
    category = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=1)


class CategoryBreakdownSerializer(serializers.Serializer):
    income = CategoryEntrySerializer(many=True)
    expense = CategoryEntrySerializer(many=True)
