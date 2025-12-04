from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

from django.contrib.postgres.fields import ArrayField
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


class UserFaceProfile(models.Model):
    """
    Stores AWS Rekognition face data for a user.
    Backward compatible: Users can login via OTP OR face recognition.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="face_profile",
        null=True,
        blank=True,
    )
    # AWS Rekognition Face ID (returned when face is indexed)
    rekognition_face_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    # Collection ID where the face is stored (for organization)
    collection_id = models.CharField(max_length=255, default="finmate-users")
    # Whether face enrollment is complete
    is_enrolled = models.BooleanField(default=False)
    # Timestamps
    enrolled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Optional: Store phone number for lookup during face login
    # (allows face login without username if user enrolled with phone)
    phone_number = models.CharField(max_length=20, null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["phone_number"]),
            models.Index(fields=["collection_id", "is_enrolled"]),
        ]

    def __str__(self) -> str:
        return f"Face profile for {self.user.username if self.user else 'Unknown'} ({'enrolled' if self.is_enrolled else 'pending'})"
