from django.db import migrations


ROLE_SEED_DATA = [
    ("viewer", "Can only view dashboard data."),
    ("analyst", "Can view records and access insights."),
    ("admin", "Full access to manage records and users."),
]


def seed_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")

    for name, description in ROLE_SEED_DATA:
        Role.objects.get_or_create(
            name=name,
            defaults={"description": description},
        )


def unseed_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")

    role_names = [name for name, _ in ROLE_SEED_DATA]
    Role.objects.filter(name__in=role_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
    ]
