import random
from typing import Tuple

from django.conf import settings
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


def generate_otp(length: int = 6) -> str:
    start = 10 ** (length - 1)
    end = (10**length) - 1
    return str(random.randint(start, end))


def send_otp_via_twilio(phone_number: str, otp_code: str) -> Tuple[bool, str]:
    # Validate Twilio credentials
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        return False, "Twilio credentials are not configured. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in your environment variables."
    
    # Validate that either messaging service or phone number is set
    if not settings.TWILIO_MESSAGING_SERVICE_SID and not settings.DEFAULT_FROM_PHONE_NUMBER:
        return False, "Twilio messaging configuration is missing. Please set either TWILIO_MESSAGING_SERVICE_SID or DEFAULT_FROM_PHONE_NUMBER in your environment variables."

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        body = f"Your login verification code is {otp_code}."

        if settings.TWILIO_MESSAGING_SERVICE_SID:
            client.messages.create(
                messaging_service_sid=settings.TWILIO_MESSAGING_SERVICE_SID,
                to=phone_number,
                body=body,
            )
        else:
            client.messages.create(
                from_=settings.DEFAULT_FROM_PHONE_NUMBER,
                to=phone_number,
                body=body,
            )
    except TwilioRestException as exc:
        error_msg = str(exc)
        # Provide more user-friendly error messages
        if "20003" in error_msg or "Authenticate" in error_msg:
            return False, "Twilio authentication failed. Please check your TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN credentials."
        elif "21211" in error_msg:
            return False, f"Invalid phone number format: {phone_number}"
        elif "21608" in error_msg:
            return False, "The phone number is not verified for your Twilio account. Please verify it in the Twilio console."
        else:
            return False, f"Twilio error: {error_msg}"
    except Exception as exc:
        return False, f"Unexpected error while sending OTP: {str(exc)}"

    return True, "OTP sent successfully."

