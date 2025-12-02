import json
import logging

from django.conf import settings
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import api_view, permission_classes, parser_classes
from typing import Optional

from finance.models import UHFSScore
from finance.services.uhfs import calculate_and_store_uhfs
from finance.services.products_util import get_suggested_products_util
from finance.serializers import ProductSerializer
from training.models import TrainingSection

from .models import ChatSession, ChatMessage, ChatAttachment
from .serializers import (
    ChatSessionSerializer,
    ChatMessageSerializer,
    FinMateChatRequestSerializer,
)

from openai import OpenAI
import boto3
import uuid
import time
import requests
from django.http import HttpResponse

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


def _get_training_sections_context():
    """
    Provide active training sections so FinMate can recommend the right modules.
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
    """
    System prompt for responsible FinMate behaviour.
    """
    prompt = (
        "You are FinMate, an AI-powered financial coach for Indian gig workers and low-"
        "income users. You must:\n"
        "- Use simple, friendly language (English, can mix basic Hindi words if helpful).\n"
        "- If UHFS score is present in the context, explicitly say: "
        "  \"Your UHFS score is X \" and explain briefly what that means.\n"
        "- Explain UHFS components clearly and concretely (income stability, financial access, "
        "  resilience, protection, literacy).\n"
        "- NEVER give investment, tax, or legal advice as guaranteed. Always say it is "
        "  educational and suggest consulting a human advisor for final decisions.\n"
        "- Avoid obscene, hateful, sexual, or unsafe content. If user asks for that, refuse "
        "  politely and redirect to financial topics. Always suggest products from the "
        "  database Product table first, then suggest any general products. The suggested "
        "  products are got via suggested product API call.\n"
        "- When you mention products, explain why they match the user's UHFS profile.\n"
        "- Always give 2–4 specific next steps the user can take this week. Also, always give "
        "  the products in the suggested products list in the response and then any other "
        "  products that are not in the suggested products list in the response. Also suggest "
        "  how to improve the score by completing Financial Health trainings and simple habits.\n"
    )
    if language_instruction:
        prompt += f"- {language_instruction.strip()}.\n"
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


def _ensure_chat_session(user, session_id=None):
    """
    Fetch an existing chat session or create a new one with UHFS context.
    """
    if session_id:
        try:
            return ChatSession.objects.get(id=session_id, user=user)
        except ChatSession.DoesNotExist:
            raise ChatSession.DoesNotExist("Session not found")

    uhfs_score, uhfs_components, overall_risk, suggested_products = _get_uhfs_and_products(user)
    return ChatSession.objects.create(
        user=user,
        title=f"FinMate session {timezone.now().date()}",
        uhfs_score=uhfs_score,
        uhfs_components=uhfs_components,
        uhfs_overall_risk=overall_risk,
        suggested_products_snapshot=suggested_products,
    )


def _generate_finmate_ai_reply(session, message_text, language_instruction=None):
    """
    Generate AI reply using the shared FinMate logic.
    """
    from .rag_retriever import retrieve_relevant_chunks

    context_block = _build_context_block(
        session.uhfs_score,
        session.uhfs_components,
        session.uhfs_overall_risk,
        session.suggested_products_snapshot or [],
        training_sections=_get_training_sections_context(),
    )

    # RAG: retrieve relevant knowledge snippets based on question + UHFS context
    retrieval_query = (
        f"User question: {message_text}\n"
        f"UHFS score: {context_block.get('uhfs_score')}\n"
        f"Components: {context_block.get('uhfs_components')}\n"
        "Retrieve documents that explain this situation and suggest suitable products "
        "and training modules to improve the user's UHFS."
    )
    try:
        retrieved_docs = retrieve_relevant_chunks(retrieval_query, top_k=5)
    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}")
        retrieved_docs = []

    retrieved_text_block = ""
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
    messages.append(
        {
            "role": "system",
            "content": system_context,
        }
    )
    messages.extend(history)
    if not history or history[-1]["role"] != "user" or history[-1]["content"] != message_text:
        messages.append({"role": "user", "content": message_text})

    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key:
        logger.error("OPENAI_API_KEY is not configured in settings/env.")
        return (
            "FinMate is not fully configured on the server yet (missing AI key). "
            "Your UHFS data and products are available, but I cannot generate "
            "personalised advice until the administrator adds the AI key."
        )

    client = OpenAI(api_key=api_key)
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

    return reply_text


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

        # Generate AI reply (uses RAG + UHFS/products/training context)
        reply_text = _generate_finmate_ai_reply(session, message_text)

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


# ---- AWS Voice-to-Finance Assistant ----

AWS_REGION = getattr(settings, "AWS_S3_REGION_NAME", "ap-south-1")
S3_BUCKET = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)

transcribe = boto3.client("transcribe", region_name=AWS_REGION)
polly = boto3.client("polly", region_name=AWS_REGION)
s3 = boto3.client("s3", region_name=AWS_REGION)

POLLY_VOICE_BY_LANGUAGE = {
    "en": "Aditi",  # Indian English
    "en-in": "Aditi",
    "en-us": "Joanna",  # US English
    "hi": "Aditi",  # Hindi (Aditi supports Hindi)
    "hi-in": "Aditi",
    "ta": "Kajal",  # Tamil
    "ta-in": "Kajal",
    "te": "Aditi",  # Telugu - fallback
    "te-in": "Aditi",
    "kn": "Aditi",  # Kannada - fallback
    "kn-in": "Aditi",
    "ml": "Aditi",  # Malayalam - fallback
    "ml-in": "Aditi",
    "pa": "Aditi",  # Punjabi - fallback
    "pa-in": "Aditi",
    "bn": "Aditi",  # Bengali - fallback
    "bn-in": "Aditi",
}
DEFAULT_POLLY_VOICE = "Aditi"

# Voices that require neural engine
NEURAL_VOICES = ["Kajal"]

LANGUAGE_DISPLAY_NAMES = {
    "EN-IN": "English",
    "EN-US": "English",
    "HI-IN": "Hindi",
    "TA-IN": "Tamil",
    "TE-IN": "Telugu",
    "KN-IN": "Kannada",
    "ML-IN": "Malayalam",
    "PA-IN": "Punjabi",
    "BN-IN": "Bengali",
}

TRANSCRIBE_LANGUAGE_OPTIONS = [
    "hi-IN",
    "en-IN",
    "en-US",
    "ta-IN",
    "te-IN",
    "kn-IN",
    "ml-IN",
    "pa-IN",
    "bn-IN",
]


def _get_language_instruction(language_code: Optional[str]) -> Optional[str]:
    if not language_code:
        return None
    display = LANGUAGE_DISPLAY_NAMES.get(language_code.upper(), "the user's language")
    return f"Respond in {display}"


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def voice_to_finance(request):
    """
    POST /api/aichat/voice/ask
    Form-data: audio=@sample_voice.wav

    - Uploads audio to S3
    - Runs Amazon Transcribe with auto language detection
    - Generates FinMate advice using the same logic as /finmate/chat/
    - Synthesizes the reply using Polly in the detected/requested language
    - Returns MP3 audio with helpful headers (text, language, session id)
    """
    data = request.data
    audio_file = request.FILES.get("audio")
    if not audio_file:
        return Response({"error": "audio file required as 'audio'"}, status=400)

    if not S3_BUCKET:
        return Response({"error": "AWS_STORAGE_BUCKET_NAME not configured"}, status=500)

    # Check AWS credentials are configured
    aws_access_key = getattr(settings, "AWS_ACCESS_KEY_ID", None)
    aws_secret_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
    if not aws_access_key or not aws_secret_key:
        return Response(
            {
                "error": "AWS credentials not configured",
                "details": "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in environment/settings.",
            },
            status=500,
        )

    # Validate file size (max 25MB for audio files)
    MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB
    if audio_file.size > MAX_AUDIO_SIZE:
        return Response(
            {
                "error": "File too large",
                "message": f"Audio file size ({audio_file.size / (1024*1024):.2f} MB) exceeds maximum allowed size (25 MB).",
                "max_size_mb": 25,
                "received_size_mb": round(audio_file.size / (1024 * 1024), 2),
            },
            status=413,
        )

    # Validate file type (log warning but allow uncommon types)
    allowed_types = ["audio/wav", "audio/wave", "audio/x-wav", "audio/mpeg", "audio/mp3", "audio/mp4", "audio/m4a"]
    if audio_file.content_type not in allowed_types:
        logger.warning(f"Unexpected content type: {audio_file.content_type}")

    # Ensure chat session (reuse if session_id provided)
    session_id = data.get("session_id")
    try:
        session = _ensure_chat_session(request.user, session_id=session_id)
    except ChatSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=404)

    requested_voice_id = data.get("voice_id")
    requested_language = data.get("language")
    voice_id = requested_voice_id or DEFAULT_POLLY_VOICE

    file_name = f"voice_inputs/{uuid.uuid4()}.wav"

    # Upload audio to S3 with error handling
    try:
        audio_file.seek(0)
        s3.upload_fileobj(
            audio_file,
            S3_BUCKET,
            file_name,
            ExtraArgs={"ContentType": getattr(audio_file, "content_type", "audio/wav")},
        )
        logger.info(f"Successfully uploaded {file_name} to S3 bucket {S3_BUCKET}")
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")
        error_msg = str(e)
        if "AccessDenied" in error_msg or "Access Denied" in error_msg:
            return Response(
                {
                    "error": "S3 Access Denied",
                    "message": "Your AWS credentials do not have permission to upload to S3.",
                    "required_permissions": [
                        "s3:PutObject",
                        "s3:GetObject",
                        "s3:CreateMultipartUpload",
                        "s3:AbortMultipartUpload",
                    ],
                    "bucket": S3_BUCKET,
                    "region": AWS_REGION,
                    "fix": "Add these permissions to your IAM user/role policy, or check bucket policy.",
                },
                status=403,
            )
        elif "NoSuchBucket" in error_msg:
            return Response(
                {
                    "error": f"S3 bucket '{S3_BUCKET}' does not exist",
                    "message": "The configured bucket name does not exist or is not accessible.",
                    "bucket": S3_BUCKET,
                    "region": AWS_REGION,
                    "fix": "Verify AWS_STORAGE_BUCKET_NAME in settings matches an existing bucket.",
                },
                status=404,
            )
        elif "InvalidAccessKeyId" in error_msg or "SignatureDoesNotMatch" in error_msg:
            return Response(
                {
                    "error": "Invalid AWS credentials",
                    "message": "The AWS access key ID or secret key is incorrect.",
                    "fix": "Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in settings.",
                },
                status=401,
            )
        else:
            return Response(
                {
                    "error": f"S3 upload failed: {error_msg}",
                    "message": "Please check AWS credentials and bucket configuration.",
                    "bucket": S3_BUCKET,
                    "region": AWS_REGION,
                },
                status=500,
            )

    job_name = f"transcribe_{uuid.uuid4()}"

    # Start Amazon Transcribe Job with auto language detection
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": f"s3://{S3_BUCKET}/{file_name}"},
        MediaFormat="wav",
        IdentifyLanguage=True,
        LanguageOptions=TRANSCRIBE_LANGUAGE_OPTIONS,
    )

    # Simple polling (hackathon style)
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        state = status["TranscriptionJob"]["TranscriptionJobStatus"]
        if state in ["COMPLETED", "FAILED"]:
            break
        time.sleep(1)

    if state == "FAILED":
        return Response({"error": "Transcription failed"}, status=500)

    detected_language = status["TranscriptionJob"].get("LanguageCode", "en-IN")
    logger.info(f"Detected language: {detected_language}")

    transcript_url = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
    transcript_json = requests.get(transcript_url).json()
    text = (transcript_json["results"]["transcripts"][0].get("transcript") or "").strip()

    if not text:
        return Response({"error": "Could not transcribe the audio. Please try again with a clearer recording."}, status=400)

    # Determine final response language & voice
    response_language_code = (requested_language or detected_language or "en-IN").upper()
    language_instruction = _get_language_instruction(response_language_code)

    if not requested_voice_id:
        normalized_lang = response_language_code.lower()
        voice_id = POLLY_VOICE_BY_LANGUAGE.get(normalized_lang) or POLLY_VOICE_BY_LANGUAGE.get(
            normalized_lang.split("-")[0], DEFAULT_POLLY_VOICE
        )
        logger.info(f"Auto-selected voice {voice_id} for language {response_language_code}")

    # Save user message (transcribed text)
    user_msg = ChatMessage.objects.create(
        session=session,
        role="user",
        content=text,
    )

    # Generate FinMate reply (same logic as chat API)
    advice = _generate_finmate_ai_reply(session, text, language_instruction=language_instruction)

    assistant_msg = ChatMessage.objects.create(
        session=session,
        role="assistant",
        content=advice,
    )

    # Convert advice to speech via Polly
    engine = "neural" if voice_id in NEURAL_VOICES else "standard"

    try:
        polly_audio = polly.synthesize_speech(
            Text=advice,
            VoiceId=voice_id,
            OutputFormat="mp3",
            Engine=engine,
        )
        audio_stream = polly_audio["AudioStream"].read()
    except Exception as e:
        logger.error(f"Error calling Polly with {engine} engine: {e}")
        if engine == "neural":
            try:
                logger.info(f"Retrying with standard engine for voice {voice_id}")
                polly_audio = polly.synthesize_speech(
                    Text=advice,
                    VoiceId=voice_id,
                    OutputFormat="mp3",
                    Engine="standard",
                )
                audio_stream = polly_audio["AudioStream"].read()
            except Exception as e2:
                logger.error(f"Polly standard engine also failed: {e2}")
                return Response(
                    {
                        "text": advice,
                        "warning": "Polly TTS failed, returning text only.",
                        "voice_id": voice_id,
                        "error": str(e2),
                    },
                    status=200,
                )
        else:
            return Response(
                {
                    "text": advice,
                    "warning": "Polly TTS failed, returning text only.",
                    "voice_id": voice_id,
                    "error": str(e),
                },
                status=200,
            )

    response = HttpResponse(audio_stream, content_type="audio/mpeg")
    sanitized_advice = advice.replace("\n", " ").replace("\r", " ").strip()
    if len(sanitized_advice) > 500:
        sanitized_advice = sanitized_advice[:500] + "..."
    response["X-Advice-Text"] = sanitized_advice
    response["X-Polly-VoiceId"] = voice_id
    response["X-Detected-Language"] = detected_language
    response["X-Response-Language"] = response_language_code
    response["X-Session-Id"] = str(session.id)
    return response



# Create your views here.
