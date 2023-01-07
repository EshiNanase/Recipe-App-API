"""
Models for Database
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractUser, BaseUserManager, PermissionsMixin
)


class UserManager(BaseUserManager):
    """Manager fo users"""

    def create_user(self, email, name, password=None, **extra_fields):
        """Creates a user"""
        user = self.create(
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True),
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
