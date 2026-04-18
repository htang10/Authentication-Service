import random
import string
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    id = models.UUIDField(default=uuid.uuid7, editable=False, primary_key=True)

    # identity
    email = models.EmailField(max_length=255, unique=True)  # Required

    # UI
    display_name = models.CharField(max_length=255, default="")

    # authorization
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # tracking metrics
    email_verified_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Joined")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Modified At")
    last_active = models.DateTimeField(null=True)
    last_login_time = models.DateTimeField(null=True)
    last_login_ip = models.CharField(max_length=255, blank=True)
    last_login_medium = models.CharField(max_length=20, default="email")
    last_login_uagent = models.TextField(blank=True)
    last_logout_time = models.DateTimeField(null=True)
    last_logout_ip = models.CharField(max_length=255, blank=True)

    # masking
    masked_at = models.DateTimeField(null=True)

    # Suppressed fields
    last_login = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        db_table = "users"
        ordering = ["-created_at"]

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def save(self, *args, **kwargs):
        self.email = self.email.lower().strip()

        if not self.display_name:
            self.display_name = (
                self.email.split("@")[0]
                if len(self.email.split("@"))
                else "".join(random.choice(string.ascii_letters) for _ in range(6))
            )

        if self.is_superuser:
            self.is_staff = True

        super().save(**kwargs)

    def __str__(self):
        return self.email


class Token(models.Model):
    class Purpose(models.TextChoices):
        SIGN_UP = "sign_up"
        PASSWORD_RESET = "password_reset"
        EMAIL_CHANGE = "email_change"

    id = models.UUIDField(default=uuid.uuid7, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, db_index=True)  # hashed
    purpose = models.CharField(max_length=32, choices=Purpose)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Token"
        db_table = "tokens"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "purpose"]),
        ]

    def __str__(self):
        return f"{self.purpose} token for {self.user.email}"
