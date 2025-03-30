"""
Databse models.
"""
from typing import Optional, Any
from django.conf import settings
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


class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        # Defined in settings.py file - core.User
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag') # type:ignore

    # Display the title in django admin, if not will display the whole obj
    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        # Defined in settings.py file - core.User
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
