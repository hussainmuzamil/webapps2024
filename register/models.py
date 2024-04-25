from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


# Create your models here.

class PrincipalUserManager(BaseUserManager):
    def create_user(self, first_name, email, last_name=None, password=None, is_admin=None):
        if not first_name:
            raise ValueError("Users must have an first name")
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, email, password, last_name=None):
        if not first_name:
            raise ValueError("Admin must have an first name")
        if not email:
            raise ValueError("Admin must have an email address")
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class Principal(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=255, blank=True, unique=False)
    last_name = models.CharField(max_length=200, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PrincipalUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
