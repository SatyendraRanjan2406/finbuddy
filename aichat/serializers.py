from rest_framework import serializers

from .models import ChatSession, ChatMessage, ChatAttachment


class ChatAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatAttachment
        fields = ["id", "file", "original_name", "mime_type", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    attachments = ChatAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "created_at", "attachments"]
        read_only_fields = ["id", "role", "created_at", "attachments"]


class ChatSessionSerializer(serializers.ModelSerializer):
    last_messages = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = [
            "id",
            "title",
            "created_at",
            "updated_at",
            "uhfs_score",
            "uhfs_components",
            "uhfs_overall_risk",
            "suggested_products_snapshot",
            "last_messages",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "uhfs_score",
            "uhfs_components",
            "uhfs_overall_risk",
            "suggested_products_snapshot",
            "last_messages",
        ]

    def get_last_messages(self, obj):
        qs = obj.messages.order_by("-created_at")[:5]
        return ChatMessageSerializer(qs, many=True).data


class FinMateChatRequestSerializer(serializers.Serializer):
    """
    Request payload for FinMate chat.
    """

    session_id = serializers.IntegerField(required=False)
    message = serializers.CharField(allow_blank=False)


