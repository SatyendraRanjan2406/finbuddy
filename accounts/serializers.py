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


class FaceEnrollmentSerializer(serializers.Serializer):
    """
    Serializer for face enrollment (registration).
    User must be authenticated via OTP first, then enroll face.
    """
    face_image = serializers.ImageField(required=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_face_image(self, value):
        """Validate image size and format."""
        # Max 15MB (AWS Rekognition limit)
        max_size = 15 * 1024 * 1024  # 15MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Image size ({value.size / (1024*1024):.2f} MB) exceeds maximum allowed size (15 MB)."
            )
        
        # Check format
        allowed_formats = ['JPEG', 'JPG', 'PNG']
        if value.image.format not in allowed_formats:
            raise serializers.ValidationError(
                f"Image format must be one of: {', '.join(allowed_formats)}"
            )
        
        return value


class FaceLoginSerializer(serializers.Serializer):
    """
    Serializer for face login (authentication).
    User provides face image, system searches and logs them in.
    """
    face_image = serializers.ImageField(required=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_face_image(self, value):
        """Validate image size and format."""
        max_size = 15 * 1024 * 1024  # 15MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Image size ({value.size / (1024*1024):.2f} MB) exceeds maximum allowed size (15 MB)."
            )
        
        allowed_formats = ['JPEG', 'JPG', 'PNG']
        if value.image.format not in allowed_formats:
            raise serializers.ValidationError(
                f"Image format must be one of: {', '.join(allowed_formats)}"
            )
        
        return value

