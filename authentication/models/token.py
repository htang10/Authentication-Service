import uuid

from django.db import models

from authentication.models.user import User


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
