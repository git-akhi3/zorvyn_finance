from django.db import models

from apps.accounts.models.role import Role
from apps.accounts.models.user import User
from apps.core.models.base import BaseModel


class UserRole(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_role")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="user_roles")

    class Meta(BaseModel.Meta):
        db_table = "user_roles"

    def __str__(self):
        return f"{self.user.email} -> {self.role.name}"
