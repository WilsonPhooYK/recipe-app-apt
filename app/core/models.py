"""
Databse models.
"""
from typing import Optional, Any
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager['User']):
    """Manager for users."""

    def create_user(self, email:str, password:Optional[str]=None, **extra_fields: Any):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email:str, password:Optional[str]=None):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user


# AbstractBaseUser contains features for the auth feature
# PermissionsMixin contains features for permissions
class User(AbstractBaseUser, PermissionsMixin):
    """"User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Assign user manager to this class
    objects = UserManager()

    # Field to use for authenticated
    USERNAME_FIELD = 'email'
