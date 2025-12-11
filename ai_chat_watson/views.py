import logging
from typing import Optional

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from finance.models import UHFSScore
from finance.services.uhfs_v2 import calculate_and_store_uhfs
from finance.services.products_util import get_suggested_products_util
from finance.serializers import ProductSerializer
from training.models import TrainingSection

from .models import WatsonChatSession, WatsonChatMessage, WatsonChatAttachment
from .serializers import (
    WatsonChatSessionSerializer,
    WatsonChatMessageSerializer,
    WatsonChatRequestSerializer,
)
from .watson_client import send_watson_chat

logger = logging.getLogger(__name__)


def _get_uhfs_and_products(user):
    """
    Ensure UHFS score exists and fetch suggested products for context.
    """
    try:
        try:
            uhfs = UHFSScore.objects.get(user=user)
        except UHFSScore.DoesNotExist:
            calculate_and_store_uhfs(user)
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


def _get_training_sections_context():
    """
    Provide active training sections so Watson can recommend the right modules.
    """
    sections = TrainingSection.objects.filter(is_active=True).order_by("order", "id")
    context_sections = []
    for section in sections:
        context_sections.append(
            {
                "id": section.id,
                "title": section.title,
                "description": section.description or "",
                "score": section.score,
                "order": section.order,
                "content_types": section.get_available_content_types(),
                "has_video": section.has_video(),
                "has_audio": section.has_audio(),
                "has_text": section.has_text(),
            }
        )
    return context_sections


def _build_system_prompt(language_instruction=None):
    prompt = (
        "You are FinMate, now powered by IBM Watson Orchestration. "
        "Help Indian gig workers with UHFS insights, suggested products, and training guidance. "
        "Use simple language and remind that advice is educational, not guaranteed."
    )
    if language_instruction:
        prompt += f" Respond in {language_instruction}."
    return prompt


def _build_context_block(
    uhfs_score,
    uhfs_components,
    overall_risk,
    suggested_products,
    training_sections=None,
):
    return {
        "uhfs_score": uhfs_score,
        "uhfs_components": uhfs_components,
        "overall_risk": overall_risk,
        "suggested_products": suggested_products,
        "training_sections": training_sections
        if training_sections is not None
        else _get_training_sections_context(),
    }


def _ensure_session(user, session_id=None):
    if session_id:
        try:
            return WatsonChatSession.objects.get(id=session_id, user=user)
        except WatsonChatSession.DoesNotExist:
            raise WatsonChatSession.DoesNotExist("Session not found")

    uhfs_score, uhfs_components, overall_risk, suggested_products = _get_uhfs_and_products(
        user
    )
    return WatsonChatSession.objects.create(
        user=user,
        title=f"Watson chat {timezone.now().date()}",
        uhfs_score=uhfs_score,
        uhfs_components=uhfs_components,
        uhfs_overall_risk=overall_risk,
        suggested_products_snapshot=suggested_products,
    )


def _generate_watson_reply(session, message_text, language_instruction: Optional[str] = None):
    try:
        from aichat.rag_retriever import retrieve_relevant_chunks
    except Exception:
        retrieve_relevant_chunks = None

    context_block = _build_context_block(
        session.uhfs_score,
        session.uhfs_components,
        session.uhfs_overall_risk,
        session.suggested_products_snapshot or [],
        training_sections=_get_training_sections_context(),
    )

    retrieval_query = (
        f"User question: {message_text}\n"
        f"UHFS score: {context_block.get('uhfs_score')}\n"
        f"Components: {context_block.get('uhfs_components')}\n"
        "Retrieve documents that explain this situation and suggest suitable products "
        "and training modules to improve the user's UHFS."
    )
    retrieved_text_block = ""
    if retrieve_relevant_chunks:
        try:
            retrieved_docs = retrieve_relevant_chunks(retrieval_query, top_k=5)
        except Exception as e:
            logger.error(f"Watson RAG retrieval failed: {e}")
            retrieved_docs = []

        if retrieved_docs:
            chunks = []
            for d in retrieved_docs:
                title = d.get("title") or d.get("id", "")
                text = d.get("text", "")
                chunks.append(f"[{d.get('type','doc')}:{d.get('id','')}] {title}\n{text}")
            retrieved_text_block = "\n\n".join(chunks)

    history = []
    for msg in session.messages.order_by("created_at").all()[:20]:
        history.append({"role": msg.role, "content": msg.content})

    messages = [{"role": "system", "content": _build_system_prompt(language_instruction)}]
    system_context = (
        "Context JSON (UHFS + suggested products + training_sections):\n"
        f"{context_block}"
    )
    if retrieved_text_block:
        system_context += (
            "\n\nRetrieved knowledge snippets (RAG). Use these as factual references "
            "when giving advice. If something conflicts with safety or UHFS logic, "
            "prioritize safety and UHFS rules:\n"
            f"{retrieved_text_block}"
        )
    messages.append({"role": "system", "content": system_context})
    messages.extend(history)
    if not history or history[-1]["role"] != "user" or history[-1]["content"] != message_text:
        messages.append({"role": "user", "content": message_text})

    try:
        reply_text = send_watson_chat(messages, context=context_block, temperature=0.2)
    except Exception as e:
        logger.error(f"Watson orchestration call failed: {e}")
        reply_text = (
            "I couldn't reach the Watson agent right now. "
            "Please try again later."
        )

    return reply_text


class WatsonInitView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        uhfs_score, uhfs_components, overall_risk, suggested_products = _get_uhfs_and_products(
            request.user
        )

        session = WatsonChatSession.objects.create(
            user=request.user,
            title=f"Watson chat {timezone.now().date()}",
            uhfs_score=uhfs_score,
            uhfs_components=uhfs_components,
            uhfs_overall_risk=overall_risk,
            suggested_products_snapshot=suggested_products,
        )

        data = {
            "session": WatsonChatSessionSerializer(session).data,
            "uhfs": {
                "score": uhfs_score,
                "components": uhfs_components,
                "overall_risk": overall_risk,
            },
            "suggested_products": suggested_products,
        }
        return Response(data, status=200)


class WatsonChatView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        data = request.data.copy()
        serializer = WatsonChatRequestSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        session_id = serializer.validated_data.get("session_id")
        message_text = serializer.validated_data["message"]

        try:
            session = _ensure_session(request.user, session_id=session_id)
        except WatsonChatSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=404)

        user_msg = WatsonChatMessage.objects.create(
            session=session,
            role="user",
            content=message_text,
        )

        for file_key, f in request.FILES.items():
            WatsonChatAttachment.objects.create(
                message=user_msg,
                file=f,
                original_name=getattr(f, "name", ""),
                mime_type=getattr(f, "content_type", ""),
            )

        reply_text = _generate_watson_reply(session, message_text)

        assistant_msg = WatsonChatMessage.objects.create(
            session=session,
            role="assistant",
            content=reply_text,
        )

        response_data = {
            "session": WatsonChatSessionSerializer(session).data,
            "user_message": WatsonChatMessageSerializer(user_msg).data,
            "assistant_message": WatsonChatMessageSerializer(assistant_msg).data,
        }
        return Response(response_data, status=200)

