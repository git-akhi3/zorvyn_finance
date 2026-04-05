class RecordStatus:
	PENDING = 'pending'
	COMPLETED = 'completed'
	CANCELLED = 'cancelled'

	CHOICES = [
		(PENDING, 'Pending'),
		(COMPLETED, 'Completed'),
		(CANCELLED, 'Cancelled'),
	]


class RecordType:
	INCOME = 'income'
	EXPENSE = 'expense'

	CHOICES = [
		(INCOME, 'Income'),
		(EXPENSE, 'Expense'),
	]
