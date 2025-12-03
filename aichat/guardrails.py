"""
Responsible AI guardrails for FinMate chatbot.
Includes content filtering, prompt injection detection, and response validation.
"""
import re
import logging
from typing import Dict, Tuple, Optional
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)

# Blocked patterns (obscene, hateful, unsafe content)
BLOCKED_PATTERNS = [
    r'\b(sex|porn|xxx|nude|naked|fuck|shit|damn|bitch|asshole)\b',
    r'\b(kill|murder|suicide|bomb|terrorist|violence)\b',
    r'\b(hack|crack|steal|fraud|scam|illegal)\b',
    r'\b(drug|alcohol|weed|cocaine|heroin)\b',
]

# Prompt injection patterns
PROMPT_INJECTION_PATTERNS = [
    r'ignore\s+(previous|all|above)',
    r'forget\s+(everything|all|previous)',
    r'system\s*:',
    r'you\s+are\s+now',
    r'act\s+as\s+if',
    r'pretend\s+to\s+be',
    r'roleplay\s+as',
    r'disregard\s+(instructions|rules)',
    r'new\s+instructions',
    r'override\s+(system|prompt)',
]

# Financial scam patterns
SCAM_PATTERNS = [
    r'guaranteed\s+returns?\s+of\s+\d+%',
    r'risk\s+free\s+investment',
    r'double\s+your\s+money',
    r'get\s+rich\s+quick',
    r'no\s+risk',
    r'100%\s+guaranteed',
]


def check_content_safety(text: str, check_type: str = "user") -> Tuple[bool, Optional[str]]:
    """
    Check if text contains unsafe, obscene, or inappropriate content.
    
    Args:
        text: Text to check
        check_type: "user" (input) or "assistant" (output)
    
    Returns:
        (is_safe, reason_if_unsafe)
    """
    if not text:
        return True, None
    
    text_lower = text.lower()
    
    # Check blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            reason = f"Contains inappropriate content (blocked pattern detected)"
            logger.warning(f"Content safety check failed: {reason}")
            return False, reason
    
    # Check for prompt injection (only on user input)
    if check_type == "user":
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                reason = f"Potential prompt injection attempt detected"
                logger.warning(f"Prompt injection detected: {reason}")
                return False, reason
    
    # Check for financial scams (especially in assistant output)
    if check_type == "assistant":
        for pattern in SCAM_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                reason = f"Response contains potentially misleading financial claims"
                logger.warning(f"Scam pattern detected in assistant response: {reason}")
                return False, reason
    
    return True, None


def validate_financial_advice(response: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that financial advice is responsible and doesn't make guarantees.
    
    Returns:
        (is_valid, reason_if_invalid)
    """
    if not response:
        return True, None
    
    response_lower = response.lower()
    
    # Check for guaranteed returns claims
    if re.search(r'guaranteed\s+(return|profit|income)', response_lower):
        return False, "Response makes guaranteed return claims (not allowed)"
    
    # Check for specific investment amount recommendations without disclaimers
    # (We allow general advice, but flag if it's too specific without warnings)
    if re.search(r'invest\s+₹?\s*\d+[,\d]*\s*(lakh|crore|thousand)', response_lower):
        # Check if disclaimer is present
        if not any(word in response_lower for word in ['consult', 'advisor', 'disclaimer', 'educational', 'not guaranteed']):
            return False, "Specific investment amounts without proper disclaimers"
    
    return True, None


def sanitize_user_input(user_message: str) -> Tuple[str, bool, Optional[str]]:
    """
    Sanitize and validate user input before processing.
    
    Returns:
        (sanitized_message, is_safe, reason_if_unsafe)
    """
    if not user_message:
        return "", False, "Empty message"
    
    # Basic sanitization: remove excessive whitespace, trim
    sanitized = re.sub(r'\s+', ' ', user_message.strip())
    
    # Check content safety
    is_safe, reason = check_content_safety(sanitized, check_type="user")
    
    if not is_safe:
        return sanitized, False, reason
    
    # Limit message length (prevent abuse)
    MAX_MESSAGE_LENGTH = 2000
    if len(sanitized) > MAX_MESSAGE_LENGTH:
        sanitized = sanitized[:MAX_MESSAGE_LENGTH]
        logger.warning(f"User message truncated from {len(user_message)} to {MAX_MESSAGE_LENGTH} chars")
    
    return sanitized, True, None


def validate_assistant_response(response: str) -> Tuple[bool, Optional[str]]:
    """
    Validate assistant response for safety and compliance.
    
    Returns:
        (is_valid, reason_if_invalid)
    """
    if not response:
        return False, "Empty response"
    
    # Check content safety
    is_safe, reason = check_content_safety(response, check_type="assistant")
    if not is_safe:
        return False, reason
    
    # Validate financial advice
    is_valid_advice, advice_reason = validate_financial_advice(response)
    if not is_valid_advice:
        return False, advice_reason
    
    return True, None


def get_safe_fallback_message(user_language: str = "en") -> str:
    """
    Return a safe, generic fallback message when content is blocked.
    """
    fallbacks = {
        "en": (
            "I understand you're asking about financial topics. "
            "Let me help you with your UHFS score, suggested products, or training modules. "
            "How can I assist you with your financial health today?"
        ),
        "hi": (
            "मैं समझ गया कि आप वित्तीय विषयों के बारे में पूछ रहे हैं। "
            "मैं आपकी UHFS स्कोर, सुझाए गए उत्पादों, या प्रशिक्षण मॉड्यूल के साथ मदद कर सकता हूं। "
            "आज मैं आपकी वित्तीय सेहत के साथ कैसे मदद कर सकता हूं?"
        ),
        "ta": (
            "நீங்கள் நிதி தலைப்புகள் பற்றி கேட்கிறீர்கள் என்பதை நான் புரிந்துகொண்டேன். "
            "உங்கள் UHFS மதிப்பெண், பரிந்துரைக்கப்பட்ட தயாரிப்புகள் அல்லது பயிற்சி தொகுதிகளுடன் நான் உதவ முடியும். "
            "இன்று உங்கள் நிதி ஆரோக்கியத்துடன் நான் எவ்வாறு உதவ முடியும்?"
        ),
    }
    
    lang_code = user_language.split("-")[0] if "-" in user_language else user_language
    return fallbacks.get(lang_code, fallbacks["en"])


def moderate_with_openai(text: str, check_type: str = "user") -> Tuple[bool, Optional[str]]:
    """
    Use OpenAI moderation API for additional safety check.
    Falls back to pattern-based checks if API is unavailable.
    
    Returns:
        (is_safe, reason_if_unsafe)
    """
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key:
        # Fallback to pattern-based checks
        return check_content_safety(text, check_type)
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.moderations.create(input=text)
        
        result = response.results[0]
        if result.flagged:
            categories = [cat for cat, flagged in result.categories.__dict__.items() if flagged]
            reason = f"OpenAI moderation flagged: {', '.join(categories)}"
            logger.warning(f"OpenAI moderation flagged content: {reason}")
            return False, reason
        
        return True, None
    except Exception as e:
        logger.error(f"OpenAI moderation API error: {e}, falling back to pattern checks")
        return check_content_safety(text, check_type)

