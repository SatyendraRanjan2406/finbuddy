import re

from rest_framework import serializers


PHONE_REGEX = re.compile(r"^\+?\d{10,15}$")


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value: str) -> str:
        cleaned = value.strip()
        if not PHONE_REGEX.match(cleaned):
            raise serializers.ValidationError(
                "Phone number must include country code and contain 10-15 digits."
            )
        if not cleaned.startswith("+"):
            cleaned = f"+{cleaned}"
        return cleaned


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(min_length=4, max_length=6)

    def validate_phone_number(self, value: str) -> str:
        return SendOTPSerializer().validate_phone_number(value)

