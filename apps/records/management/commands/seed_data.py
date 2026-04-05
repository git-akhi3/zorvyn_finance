"""
Populates the database with realistic test data
for manual API testing via Swagger or Postman.
Safe to run multiple times.
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Role, User, UserRole
from apps.records.constants import RecordStatus, RecordType
from apps.records.models import FinancialRecord


class Command(BaseCommand):
    help = "Seeds realistic test data for API testing."

    USERS = [
        {
            "email": "admin@zorvyn.com",
            "password": "Admin@1234",
            "first_name": "Arjun",
            "last_name": "Mehta",
            "role": Role.ADMIN,
        },
        {
            "email": "analyst@zorvyn.com",
            "password": "Analyst@1234",
            "first_name": "Priya",
            "last_name": "Sharma",
            "role": Role.ANALYST,
        },
        {
            "email": "viewer@zorvyn.com",
            "password": "Viewer@1234",
            "first_name": "Rohan",
            "last_name": "Verma",
            "role": Role.VIEWER,
        },
    ]

    RECORDS = [
        {
            "amount": "150000.00",
            "type": RecordType.INCOME,
            "category": "Client Payment",
            "status": RecordStatus.COMPLETED,
            "notes": "Q1 consulting fee from Infosys",
        },
        {
            "amount": "85000.00",
            "type": RecordType.INCOME,
            "category": "Product Sales",
            "status": RecordStatus.COMPLETED,
            "notes": "SaaS subscription revenue March",
        },
        {
            "amount": "45000.00",
            "type": RecordType.INCOME,
            "category": "Client Payment",
            "status": RecordStatus.PENDING,
            "notes": "Invoice #1042 pending clearance",
        },
        {
            "amount": "200000.00",
            "type": RecordType.INCOME,
            "category": "Investment",
            "status": RecordStatus.COMPLETED,
            "notes": "Seed round tranche 2 received",
        },
        {
            "amount": "32000.00",
            "type": RecordType.INCOME,
            "category": "Freelance",
            "status": RecordStatus.COMPLETED,
            "notes": "UI audit project TechCorp",
        },
        {
            "amount": "67500.00",
            "type": RecordType.INCOME,
            "category": "Product Sales",
            "status": RecordStatus.COMPLETED,
            "notes": "Enterprise licence renewal",
        },
        {
            "amount": "15000.00",
            "type": RecordType.INCOME,
            "category": "Referral",
            "status": RecordStatus.PENDING,
            "notes": "Partner referral bonus Q2",
        },
        {
            "amount": "92000.00",
            "type": RecordType.INCOME,
            "category": "Client Payment",
            "status": RecordStatus.COMPLETED,
            "notes": "Final milestone payment Razorpay project",
        },
        {
            "amount": "28000.00",
            "type": RecordType.INCOME,
            "category": "Grants",
            "status": RecordStatus.COMPLETED,
            "notes": "Startup India grant disbursement",
        },
        {
            "amount": "110000.00",
            "type": RecordType.INCOME,
            "category": "Product Sales",
            "status": RecordStatus.COMPLETED,
            "notes": "Annual plan renewals batch April",
        },
        {
            "amount": "55000.00",
            "type": RecordType.EXPENSE,
            "category": "Salaries",
            "status": RecordStatus.COMPLETED,
            "notes": "Engineering team March payroll",
        },
        {
            "amount": "12000.00",
            "type": RecordType.EXPENSE,
            "category": "Infrastructure",
            "status": RecordStatus.COMPLETED,
            "notes": "AWS EC2 and RDS monthly bill",
        },
        {
            "amount": "8500.00",
            "type": RecordType.EXPENSE,
            "category": "Marketing",
            "status": RecordStatus.COMPLETED,
            "notes": "Google Ads campaign March",
        },
        {
            "amount": "45000.00",
            "type": RecordType.EXPENSE,
            "category": "Salaries",
            "status": RecordStatus.COMPLETED,
            "notes": "Design team March payroll",
        },
        {
            "amount": "3200.00",
            "type": RecordType.EXPENSE,
            "category": "Software",
            "status": RecordStatus.COMPLETED,
            "notes": "Figma and Linear annual licences",
        },
        {
            "amount": "18000.00",
            "type": RecordType.EXPENSE,
            "category": "Operations",
            "status": RecordStatus.PENDING,
            "notes": "Office rent April",
        },
        {
            "amount": "6700.00",
            "type": RecordType.EXPENSE,
            "category": "Travel",
            "status": RecordStatus.COMPLETED,
            "notes": "Client visit Bangalore flights and hotel",
        },
        {
            "amount": "9200.00",
            "type": RecordType.EXPENSE,
            "category": "Marketing",
            "status": RecordStatus.CANCELLED,
            "notes": "Conference sponsorship cancelled",
        },
        {
            "amount": "22000.00",
            "type": RecordType.EXPENSE,
            "category": "Infrastructure",
            "status": RecordStatus.COMPLETED,
            "notes": "Cloudflare and Vercel annual plans",
        },
        {
            "amount": "4500.00",
            "type": RecordType.EXPENSE,
            "category": "Legal",
            "status": RecordStatus.COMPLETED,
            "notes": "Contract review retainer fee",
        },
        {
            "amount": "75000.00",
            "type": RecordType.EXPENSE,
            "category": "Salaries",
            "status": RecordStatus.COMPLETED,
            "notes": "Product team April payroll",
        },
        {
            "amount": "11000.00",
            "type": RecordType.EXPENSE,
            "category": "Operations",
            "status": RecordStatus.COMPLETED,
            "notes": "Stationery and office supplies Q1",
        },
        {
            "amount": "5600.00",
            "type": RecordType.EXPENSE,
            "category": "Software",
            "status": RecordStatus.PENDING,
            "notes": "New team Slack seats",
        },
        {
            "amount": "31000.00",
            "type": RecordType.EXPENSE,
            "category": "Marketing",
            "status": RecordStatus.COMPLETED,
            "notes": "Content agency retainer April",
        },
        {
            "amount": "14500.00",
            "type": RecordType.EXPENSE,
            "category": "Infrastructure",
            "status": RecordStatus.COMPLETED,
            "notes": "Database migration and backup setup",
        },
        {
            "amount": "2800.00",
            "type": RecordType.EXPENSE,
            "category": "Travel",
            "status": RecordStatus.COMPLETED,
            "notes": "Team offsite local transport",
        },
        {
            "amount": "19500.00",
            "type": RecordType.EXPENSE,
            "category": "Legal",
            "status": RecordStatus.COMPLETED,
            "notes": "IP filing fees",
        },
        {
            "amount": "7800.00",
            "type": RecordType.EXPENSE,
            "category": "Operations",
            "status": RecordStatus.COMPLETED,
            "notes": "Courier and logistics Q1",
        },
        {
            "amount": "42000.00",
            "type": RecordType.EXPENSE,
            "category": "Salaries",
            "status": RecordStatus.COMPLETED,
            "notes": "Intern stipends batch February",
        },
        {
            "amount": "16000.00",
            "type": RecordType.EXPENSE,
            "category": "Marketing",
            "status": RecordStatus.COMPLETED,
            "notes": "LinkedIn ads B2B campaign",
        },
    ]

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding test data...")

        admin_user = self._seed_users()
        self._seed_records(admin_user)

        self.stdout.write(
            self.style.SUCCESS(
                "\nSeed complete. Login credentials:\n"
                "  Admin:    admin@zorvyn.com    / Admin@1234\n"
                "  Analyst:  analyst@zorvyn.com  / Analyst@1234\n"
                "  Viewer:   viewer@zorvyn.com   / Viewer@1234\n"
                "\nSwagger UI: http://127.0.0.1:8000/api/docs/"
            )
        )

    def _seed_users(self):
        admin_user = None
        for user_data in self.USERS:
            role_name = user_data["role"]
            password = user_data["password"]

            role = Role.objects.filter(name=role_name).first()
            if role is None:
                self.stdout.write(
                    self.style.ERROR(
                        f"  Role '{role_name}' not found. Run migrations to apply role seed data."
                    )
                )
                continue

            user, created = User.all_objects.get_or_create(
                email=user_data["email"],
                defaults={
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "is_active": True,
                },
            )

            if created:
                user.set_password(password)
                user.save(update_fields=["password", "updated_at"])
                self.stdout.write(self.style.SUCCESS(f"  Created {role_name}: {user.email}"))
            else:
                self.stdout.write(f"  User exists, skipping: {user.email}")

            UserRole.objects.update_or_create(user=user, defaults={"role": role})

            if role_name == Role.ADMIN:
                admin_user = user

        return admin_user

    def _seed_records(self, admin_user):
        if not admin_user:
            self.stdout.write(self.style.WARNING("  Admin user not found, skipping records."))
            return

        today = timezone.now().date()
        random.seed(42)

        for index, record_data in enumerate(self.RECORDS, start=1):
            days_back = random.randint(0, 180)
            record_date = today - timedelta(days=days_back)
            reference_number = f"SEED-TXN-{index:04d}"

            FinancialRecord.all_objects.update_or_create(
                reference_number=reference_number,
                defaults={
                    "amount": Decimal(record_data["amount"]),
                    "type": record_data["type"],
                    "category": record_data["category"],
                    "date": record_date,
                    "notes": record_data["notes"],
                    "currency": "INR",
                    "status": record_data["status"],
                    "created_by": admin_user,
                    "is_deleted": False,
                    "deleted_at": None,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"  Upserted {len(self.RECORDS)} financial records"))
