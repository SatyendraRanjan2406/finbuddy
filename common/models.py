from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Common base model with created_at / updated_at"""
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserOwnedModel(models.Model):
    """Base for any table that belongs to a user"""
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    class Meta:
        abstract = True
