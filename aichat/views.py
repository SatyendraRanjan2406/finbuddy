import logging

from django.conf import settings
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from finance.models import UHFSScore
from finance.services.uhfs import calculate_and_store_uhfs
from finance.services.products_util import get_suggested_products_util
from finance.serializers import ProductSerializer

from .models import ChatSession, ChatMessage, ChatAttachment
from .serializers import (
    ChatSessionSerializer,
    ChatMessageSerializer,
    FinMateChatRequestSerializer,
)

from openai import OpenAI

logger = logging.getLogger(__name__)


def _get_uhfs_and_products(user):
    """
    Helper to ensure UHFS score exists and fetch suggested products for context.
    """
    try:
        try:
            uhfs = UHFSScore.objects.get(user=user)
        except UHFSScore.DoesNotExist:
            result = calculate_and_store_uhfs(user)
            uhfs = UHFSScore.objects.get(user=user)
    except Exception as e:
        logger.error(f"Error calculating UHFS for user {user.id}: {e}")
        uhfs = None

    uhfs_score = uhfs.score if uhfs else None
    uhfs_components = uhfs.components if uhfs else None
    overall_risk = uhfs.overall_risk if uhfs else None

    suggested_products = []
    if uhfs_score is not None:
        try:
            products_qs = get_suggested_products_util(uhfs_score)
            suggested_products = ProductSerializer(products_qs, many=True).data
        except Exception as e:
            logger.error(f"Error fetching suggested products: {e}")

    return uhfs_score, uhfs_components, overall_risk, suggested_products


def _build_system_prompt():
    """
    System prompt for responsible FinMate behaviour.
    """
    return (
        "You are FinMate, an AI-powered financial coach for Indian gig workers and low-"
        "income users. You must:\n"
        "- Use **simple, friendly language** (English, can mix basic Hindi words if helpful).\n"
        "- Explain UHFS components clearly and concretely.\n"
        "- NEVER give investment, tax, or legal advice as guaranteed. Always say it is\n"
        "  educational and suggest consulting a human advisor for final decisions.\n"
        "- Avoid obscene, hateful, sexual, or unsafe content. If user asks for that, refuse\n"
        "  politely and redirect to financial topics.\n"
        "- When you mention products, explain **why** they match the user's UHFS profile.\n"
        "- Always give **2–4 specific next steps** the user can take this week.\n"
    )


def _build_context_block(uhfs_score, uhfs_components, overall_risk, suggested_products):
    return {
        "uhfs_score": uhfs_score,
        "uhfs_components": uhfs_components,
        "overall_risk": overall_risk,
        "suggested_products": suggested_products,
    }


class FinMateInitView(APIView):
    """
    GET /api/aichat/finmate/init/
    Returns UHFS breakdown + suggested products + creates a chat session.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        uhfs_score, uhfs_components, overall_risk, suggested_products = _get_uhfs_and_products(
            request.user
        )

        session = ChatSession.objects.create(
            user=request.user,
            title=f"FinMate session {timezone.now().date()}",
            uhfs_score=uhfs_score,
            uhfs_components=uhfs_components,
            uhfs_overall_risk=overall_risk,
            suggested_products_snapshot=suggested_products,
        )

        data = {
            "session": ChatSessionSerializer(session).data,
            "uhfs": {
                "score": uhfs_score,
                "components": uhfs_components,
                "overall_risk": overall_risk,
            },
            "suggested_products": suggested_products,
        }
        return Response(data, status=200)


class FinMateChatView(APIView):
    """
    POST /api/aichat/finmate/chat/
    Chat with FinMate, with UHFS + product context and optional file attachments.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        # Handle JSON and multipart uniformly
        data = request.data.copy()
        serializer = FinMateChatRequestSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        session_id = serializer.validated_data.get("session_id")
        message_text = serializer.validated_data["message"]

        # Ensure session
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return Response({"error": "Session not found"}, status=404)
        else:
            uhfs_score, uhfs_components, overall_risk, suggested_products = _get_uhfs_and_products(
                request.user
            )
            session = ChatSession.objects.create(
                user=request.user,
                title=f"FinMate session {timezone.now().date()}",
                uhfs_score=uhfs_score,
                uhfs_components=uhfs_components,
                uhfs_overall_risk=overall_risk,
                suggested_products_snapshot=suggested_products,
            )

        # Save user message
        user_msg = ChatMessage.objects.create(
            session=session,
            role="user",
            content=message_text,
        )

        # Save attachments if any
        for file_key, f in request.FILES.items():
            ChatAttachment.objects.create(
                message=user_msg,
                file=f,
                original_name=getattr(f, "name", ""),
                mime_type=getattr(f, "content_type", ""),
            )

        # Prepare OpenAI client
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            logger.error("OPENAI_API_KEY is not configured in settings/env.")
            reply_text = (
                "FinMate is not fully configured on the server yet (missing AI key). "
                "Your UHFS data and products are available, but I cannot generate "
                "personalised advice until the administrator adds the AI key."
            )
            assistant_msg = ChatMessage.objects.create(
                session=session,
                role="assistant",
                content=reply_text,
            )
            response_data = {
                "session": ChatSessionSerializer(session).data,
                "user_message": ChatMessageSerializer(user_msg).data,
                "assistant_message": ChatMessageSerializer(assistant_msg).data,
            }
            return Response(response_data, status=500)

        client = OpenAI(api_key=api_key)

        context_block = _build_context_block(
            session.uhfs_score,
            session.uhfs_components,
            session.uhfs_overall_risk,
            session.suggested_products_snapshot or [],
        )

        # Build conversation history (last 10 messages)
        history = []
        for msg in session.messages.order_by("created_at").all()[:20]:
            history.append({"role": msg.role, "content": msg.content})

        # Ensure system prompt at top
        messages = [{"role": "system", "content": _build_system_prompt()}]
        messages.append(
            {
                "role": "system",
                "content": (
                    "Context JSON (UHFS + suggested products):\n"
                    f"{context_block}"
                ),
            }
        )
        messages.extend(history)
        messages.append({"role": "user", "content": message_text})

        try:
            completion = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=600,
            )
            reply_text = completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            reply_text = (
                "I am unable to reach the FinMate brain right now. "
                "Please try again later, and meanwhile you can still "
                "focus on tracking your expenses and building a small emergency buffer."
            )

        # Save assistant reply
        assistant_msg = ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=reply_text,
        )

        response_data = {
            "session": ChatSessionSerializer(session).data,
            "user_message": ChatMessageSerializer(user_msg).data,
            "assistant_message": ChatMessageSerializer(assistant_msg).data,
        }
        return Response(response_data, status=200)


# Create your views here.
