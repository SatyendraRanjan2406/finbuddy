from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import PhoneOTP
from accounts.serializers import SendOTPSerializer, VerifyOTPSerializer
from accounts.services import generate_otp, send_otp_via_twilio


User = get_user_model()


class SendOTPView(APIView):
    """
    POST /api/auth/send-otp
    """

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        otp_code = generate_otp()

        # Delete any existing OTP for this phone number to ensure
        # created_at is properly reset (since it has auto_now_add=True)
        PhoneOTP.objects.filter(phone_number=phone_number).delete()
        
        # Create a new OTP entry with fresh timestamp
        otp_entry = PhoneOTP.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            is_verified=False,
        )

        is_sent, message = send_otp_via_twilio(phone_number, otp_code)
        if not is_sent:
            return Response({"detail": message}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(
            {"detail": "OTP sent.", "otp_id": otp_entry.id},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    """
    POST /api/auth/verify-otp
    """

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        otp_code = serializer.validated_data["otp_code"]

        try:
            otp_entry = PhoneOTP.objects.get(phone_number=phone_number)
        except PhoneOTP.DoesNotExist:
            return Response(
                {"detail": "OTP not requested for this phone number."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if otp_entry.is_expired():
            return Response(
                {"detail": "OTP expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if otp_entry.otp_code != otp_code:
            return Response(
                {"detail": "Invalid OTP code."}, status=status.HTTP_400_BAD_REQUEST
            )

        otp_entry.is_verified = True
        otp_entry.save(update_fields=["is_verified"])

        user, _ = User.objects.get_or_create(
            username=phone_number,
            defaults={"is_active": True},
        )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response(
            {
                "detail": "OTP verified.",
                "access": str(access_token),
                "refresh": str(refresh),
                "user": {"id": str(user.id), "phone_number": user.username},
            },
            status=status.HTTP_200_OK,
        )
