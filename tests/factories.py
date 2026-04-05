import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import Role, User, UserRole
from apps.records.constants import RecordStatus, RecordType
from apps.records.models import FinancialRecord


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ("name",)

    name = Role.VIEWER
    description = factory.Faker("sentence")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class UserRoleFactory(DjangoModelFactory):
    class Meta:
        model = UserRole

    user = factory.SubFactory(UserFactory)
    role = factory.SubFactory(RoleFactory)


class FinancialRecordFactory(DjangoModelFactory):
    class Meta:
        model = FinancialRecord

    amount = factory.Faker("pydecimal", left_digits=6, right_digits=2, positive=True)
    type = RecordType.INCOME
    category = factory.Faker("word")
    date = factory.Faker("date_object")
    notes = factory.Faker("sentence")
    currency = "INR"
    status = RecordStatus.PENDING
    reference_number = factory.Sequence(lambda n: f"TXN-20240101-T{n:03d}")
    created_by = factory.SubFactory(UserFactory)
