from django.db import models

from apps.accounts.constants import RoleConfig
from apps.core.models.base import BaseModel


class Role(BaseModel):
    VIEWER = RoleConfig.VIEWER
    ANALYST = RoleConfig.ANALYST
    ADMIN = RoleConfig.ADMIN

    ROLE_CHOICES = RoleConfig.ROLE_CHOICES

    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)

    class Meta(BaseModel.Meta):
        db_table = "roles"

    def __str__(self):
        return self.name
