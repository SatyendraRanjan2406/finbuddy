from django.conf import settings
from django.db import models


class ChatSession(models.Model):
    """
    A FinMate conversation session per user.
    Stores a snapshot of UHFS components and suggested products used as context.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="aichat_sessions"
    )
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    uhfs_score = models.IntegerField(null=True, blank=True)
    uhfs_components = models.JSONField(null=True, blank=True)
    uhfs_overall_risk = models.CharField(max_length=50, null=True, blank=True)

    suggested_products_snapshot = models.JSONField(
        null=True,
        blank=True,
        help_text="Products snapshot used as context at session start",
    )

    def __str__(self) -> str:
        return self.title or f"FinMate Chat #{self.pk}"


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    )

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.role} @ {self.created_at}: {self.content[:40]}"


class ChatAttachment(models.Model):
    """
    Optional file attached to a chat message (image, pdf, video, etc.).
    Re-uses DEFAULT_FILE_STORAGE (e.g., S3) configuration.
    """
    message = models.ForeignKey(
        ChatMessage, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(
        upload_to="aichat/uploads/",
        null=True,
        blank=True,
    )
    original_name = models.CharField(max_length=255, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.original_name or (self.file.name if self.file else "Attachment")

