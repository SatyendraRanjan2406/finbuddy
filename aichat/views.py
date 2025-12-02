import json
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
import boto3
import uuid
import time
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator

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
        "  politely and redirect to financial topics.Always suggest products from the database Product table first  , then suggest any general products . the suggested products are got via suggested product api call. \n"
        "- When you mention products, explain **why** they match the user's UHFS profile.\n"
        "- Always give **2–4 specific next steps** the user can take this week. Also , always give the products in the suggested products list in the response and then any other products that are not in the suggested products list in the response. Also suggest to improve score by doing training in Financial Health section ,etc  tips  \n"
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


# ---- AWS Voice-to-Finance Assistant ----

AWS_REGION = getattr(settings, "AWS_S3_REGION_NAME", "ap-south-1")
S3_BUCKET = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)

transcribe = boto3.client("transcribe", region_name=AWS_REGION)
polly = boto3.client("polly", region_name=AWS_REGION)
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)
s3 = boto3.client("s3", region_name=AWS_REGION)

POLLY_VOICE_BY_LANGUAGE = {
    "en": "Aditi",  # Indian English
    "en-in": "Aditi",
    "hi": "Aditi",
    "hi-in": "Aditi",
    "ta": "Kajal",
    "ta-in": "Kajal",
    "te": "Chitra",
    "te-in": "Chitra",
    "kn": "Neerja",
    "kn-in": "Neerja",
    "ml": "Shivani",
    "ml-in": "Shivani",
    "pa": "Gurpreet",
    "pa-in": "Gurpreet",
    "bn": "Tanishaa",
    "bn-in": "Tanishaa",
}
DEFAULT_POLLY_VOICE = "Aditi"


def bedrock_finance_advice(text: str, detected_language: str = None) -> str:
    """
    Use Claude via Bedrock to generate short financial advice.
    Falls back to OpenAI if Bedrock is not available.
    Responds in the same language as the user's question.
    """
    # Map language codes to language names for the prompt
    language_names = {
        "hi-IN": "Hindi",
        "en-IN": "English",
        "en-US": "English",
        "ta-IN": "Tamil",
        "te-IN": "Telugu",
        "kn-IN": "Kannada",
        "ml-IN": "Malayalam",
        "pa-IN": "Punjabi",
        "bn-IN": "Bengali",
    }
    
    language_name = language_names.get(detected_language, "the same language as the user")
    language_instruction = f"Respond in {language_name}" if detected_language else "Respond in the same language as the user's question"
    
    prompt = f"""
        You are a financial advisor for Indian gig workers.
        User said (can be Hindi/Tamil/English/other Indian languages):
        "{text}"

        {language_instruction}.
        Provide a simple, friendly, 4-line actionable financial advice.
        Use Indian context and very practical steps.
        Avoid any obscene or unsafe content. Educational only, not guaranteed returns.
    """
    
    system_message = f"You are a financial advisor for Indian gig workers. {language_instruction}. Give simple, friendly, 4-line actionable advice in Indian context."
    
    # Try Bedrock first
    try:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 250,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )
        result_json = json.loads(response["body"].read().decode("utf-8"))
        return result_json["content"][0]["text"]
    except Exception as e:
        logger.warning(f"Bedrock failed, trying OpenAI fallback: {e}")
        
        # Fallback to OpenAI if Bedrock is not available
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if api_key:
            try:
                client = OpenAI(api_key=api_key)
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=250,
                )
                return completion.choices[0].message.content
            except Exception as openai_error:
                logger.error(f"OpenAI fallback also failed: {openai_error}")
        
        # Final fallback
        return (
            "Voice understood. Start by setting aside ₹100-200 each week as emergency savings. "
            "Track your daily expenses in a simple notebook or app. Consider opening a basic "
            "savings account if you don't have one. Build small habits for financial security."
        )


@csrf_exempt
def voice_to_finance(request):
    """
    POST /api/aichat/voice/ask
    Form-data: audio=@sample_voice.wav

    - Uploads audio to S3
    - Runs Amazon Transcribe
    - Sends text to Bedrock for advice
    - Uses Polly to synthesize advice audio
    - Returns MP3 audio with X-Advice-Text header
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    if "audio" not in request.FILES:
        return JsonResponse({"error": "audio file required as 'audio'"}, status=400)

    if not S3_BUCKET:
        return JsonResponse({"error": "AWS_STORAGE_BUCKET_NAME not configured"}, status=500)

    # Check AWS credentials are configured
    aws_access_key = getattr(settings, "AWS_ACCESS_KEY_ID", None)
    aws_secret_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
    if not aws_access_key or not aws_secret_key:
        return JsonResponse(
            {
                "error": "AWS credentials not configured",
                "details": "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in environment/settings.",
            },
            status=500,
        )

    audio_file = request.FILES["audio"]
    file_name = f"voice_inputs/{uuid.uuid4()}.wav"

    # Determine voice / language preference (optional form fields)
    requested_voice_id = request.POST.get("voice_id")
    requested_language = request.POST.get("language")
    voice_id = DEFAULT_POLLY_VOICE
    if requested_voice_id:
        voice_id = requested_voice_id
    elif requested_language:
        normalized = requested_language.lower()
        voice_id = POLLY_VOICE_BY_LANGUAGE.get(normalized) or POLLY_VOICE_BY_LANGUAGE.get(
            normalized.split("-")[0], DEFAULT_POLLY_VOICE
        )

    # Upload audio to S3 with error handling
    try:
        # Reset file pointer to beginning (in case it was read already)
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
            return JsonResponse(
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
            return JsonResponse(
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
            return JsonResponse(
                {
                    "error": "Invalid AWS credentials",
                    "message": "The AWS access key ID or secret key is incorrect.",
                    "fix": "Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in settings.",
                },
                status=401,
            )
        else:
            return JsonResponse(
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
        IdentifyLanguage=True,  # Auto-detect language
        LanguageOptions=["hi-IN", "en-IN", "en-US", "ta-IN", "te-IN", "kn-IN", "ml-IN", "pa-IN", "bn-IN"],  # Supported Indian languages
    )

    # Simple polling (hackathon style)
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        state = status["TranscriptionJob"]["TranscriptionJobStatus"]
        if state in ["COMPLETED", "FAILED"]:
            break
        time.sleep(1)

    if state == "FAILED":
        return JsonResponse({"error": "Transcription failed"}, status=500)

    # Get detected language from transcription job
    detected_language = status["TranscriptionJob"].get("LanguageCode", "en-IN")
    logger.info(f"Detected language: {detected_language}")

    transcript_url = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
    transcript_json = requests.get(transcript_url).json()
    text = transcript_json["results"]["transcripts"][0]["transcript"]

    # Auto-select voice based on detected language (override user selection if auto-detect is used)
    if not requested_voice_id:  # Only auto-select if user didn't specify
        normalized_lang = detected_language.lower()
        voice_id = POLLY_VOICE_BY_LANGUAGE.get(normalized_lang) or POLLY_VOICE_BY_LANGUAGE.get(
            normalized_lang.split("-")[0], DEFAULT_POLLY_VOICE
        )
        logger.info(f"Auto-selected voice {voice_id} for language {detected_language}")

    # Ask Bedrock for advice in the detected language
    try:
        advice = bedrock_finance_advice(text, detected_language=detected_language)
    except Exception as e:
        logger.error(f"Error calling Bedrock: {e}")
        # Fallback message in detected language
        fallback_messages = {
            "hi-IN": "आवाज समझ आ गई, लेकिन मैं अभी AI सलाहकार तक नहीं पहुंच सका। कृपया बाद में पुनः प्रयास करें, और इस बीच हर सप्ताह एक छोटी राशि आपातकालीन बचत के रूप में अलग रखना शुरू करें।",
            "ta-IN": "குரல் புரிந்தது, ஆனால் நான் இப்போது AI ஆலோசகரை அணுக முடியவில்லை. தயவுசெய்து பின்னர் மீண்டும் முயற்சிக்கவும், இதற்கிடையில் வாரத்திற்கு ஒரு சிறிய தொகையை அவசரகால சேமிப்பாக ஒதுக்கத் தொடங்குங்கள்.",
            "te-IN": "వాయిస్ అర్థమైంది, కానీ నేను ఇప్పుడు AI సలహాదారుకు చేరుకోలేకపోయాను. దయచేసి తర్వాత మళ్లీ ప్రయత్నించండి, మరియు ఈ మధ్య వారానికి ఒక చిన్న మొత్తాన్ని అత్యవసర పొదుపుగా వేరు చేయడం ప్రారంభించండి.",
            "kn-IN": "ಧ್ವನಿ ಅರ್ಥವಾಯಿತು, ಆದರೆ ನಾನು ಈಗ AI ಸಲಹೆಗಾರನನ್ನು ತಲುಪಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ, ಮತ್ತು ಈ ಮಧ್ಯೆ ವಾರಕ್ಕೆ ಒಂದು ಸಣ್ಣ ಮೊತ್ತವನ್ನು ತುರ್ತು ಉಳಿತಾಯವಾಗಿ ಬದಲಿಸಲು ಪ್ರಾರಂಭಿಸಿ।",
        }
        advice = fallback_messages.get(detected_language, 
            "Voice understood, but I could not reach the AI advisor right now. "
            "Please try again later, and meanwhile start by setting aside a small "
            "amount each week as emergency savings."
        )

    # Convert advice to speech via Polly
    # Some regional Indian voices require "neural" engine instead of "standard"
    neural_voices = ["Kajal", "Chitra", "Neerja", "Shivani", "Gurpreet", "Tanishaa"]
    engine = "neural" if voice_id in neural_voices else "standard"
    
    try:
        polly_audio = polly.synthesize_speech(
            Text=advice,
            VoiceId=voice_id,
            OutputFormat="mp3",
            Engine=engine,  # Use neural for regional Indian voices
        )
        audio_stream = polly_audio["AudioStream"].read()
    except Exception as e:
        logger.error(f"Error calling Polly with {engine} engine: {e}")
        # Try with standard engine if neural failed (fallback)
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
                return JsonResponse(
                    {
                        "text": advice,
                        "warning": "Polly TTS failed, returning text only.",
                        "voice_id": voice_id,
                        "error": str(e2),
                    },
                    status=200,
                )
        else:
            return JsonResponse(
                {
                    "text": advice,
                    "warning": "Polly TTS failed, returning text only.",
                    "voice_id": voice_id,
                    "error": str(e),
                },
                status=200,
            )

    response = HttpResponse(audio_stream, content_type="audio/mpeg")
    # Sanitize advice text for header: remove newlines and ensure single-line
    # Replace newlines with spaces, and limit length to avoid header size issues
    sanitized_advice = advice.replace("\n", " ").replace("\r", " ").strip()
    # Limit header length (HTTP headers should be < 8KB, but keep it reasonable)
    if len(sanitized_advice) > 500:
        sanitized_advice = sanitized_advice[:500] + "..."
    response["X-Advice-Text"] = sanitized_advice
    response["X-Polly-VoiceId"] = voice_id
    response["X-Detected-Language"] = detected_language
    return response



# Create your views here.
