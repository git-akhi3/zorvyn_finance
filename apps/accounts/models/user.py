from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.accounts.constants import AuthMessages
from apps.accounts.models.role import Role
from apps.core.models import BaseModel
from apps.core.utils.exceptions import InvalidInputException


class UserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise InvalidInputException(AuthMessages.EMAIL_REQUIRED)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
    all_objects = models.Manager()

    class Meta(BaseModel.Meta):
        db_table = "users"

    def __str__(self):
        return f"{self.email}"

    @property
    def role_name(self):
        try:
            return self.user_role.role.name
        except Exception:
            return Role.VIEWER

    @property
    def is_admin(self):
        return self.role_name == Role.ADMIN

    @property
    def is_analyst(self):
        return self.role_name in [Role.ANALYST, Role.ADMIN]

    @property
    def is_viewer(self):
        return self.role_name in [Role.VIEWER, Role.ANALYST, Role.ADMIN]
