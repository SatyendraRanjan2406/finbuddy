from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []


class PhoneOTP(models.Model):
    phone_number = models.CharField(max_length=15, db_index=True)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["phone_number"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.phone_number} ({'verified' if self.is_verified else 'pending'})"

    def is_expired(self) -> bool:
        expiration = self.created_at + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)
        return timezone.now() > expiration




