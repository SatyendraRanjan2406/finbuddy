import logging
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import PhoneOTP, UserFaceProfile
from finance.models import PersonalDemographic
from accounts.serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    FaceEnrollmentSerializer,
    FaceLoginSerializer,
)
from accounts.services import (
    generate_otp,
    send_otp_via_twilio,
    index_face_in_rekognition,
    search_face_in_rekognition,
    delete_face_from_rekognition,
)
from finance.utils import get_onboarding_progress_details

logger = logging.getLogger(__name__)


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

        # Get user profile data from PersonalDemographic
        mobile_number = user.phone or user.username  # Use phone field or username (which is phone_number)
        
        # Initialize user profile fields
        full_name = None
        age = None
        gender = None
        state = None
        city_district = None
        
        # Try to get data from PersonalDemographic
        try:
            personal_demo = PersonalDemographic.objects.get(user=user)
            full_name = personal_demo.full_name
            age = personal_demo.age
            gender = personal_demo.gender
            state = personal_demo.state
            city_district = personal_demo.city_district
        except PersonalDemographic.DoesNotExist:
            # Fallback to User model fields for name only
            if user.first_name or user.last_name:
                full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        
        # Get onboarding progress details
        onboarding_details = get_onboarding_progress_details(user)

        return Response(
            {
                "detail": "OTP verified.",
                "access": str(access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.id),
                    "phone_number": mobile_number,
                    "full_name": full_name,
                    "age": age,
                    "gender": gender,
                    "state": state,
                    "city_district": city_district,
                },
                "onboarding": onboarding_details,
            },
            status=status.HTTP_200_OK,
        )


class FaceEnrollmentView(APIView):
    """
    POST /api/auth/face/enroll/
    Enroll user's face for facial recognition login.
    User must be authenticated (via OTP) first.
    Backward compatible: Users can still use OTP login even after enrolling face.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = FaceEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        face_image = serializer.validated_data["face_image"]
        phone_number = serializer.validated_data.get("phone_number") or user.username

        # Read image bytes
        face_image.seek(0)
        image_bytes = face_image.read()

        # Index face in AWS Rekognition
        collection_id = "finmate-users"
        external_image_id = str(user.id)  # Use user UUID as external ID
        success, face_id, message = index_face_in_rekognition(
            image_bytes=image_bytes,
            collection_id=collection_id,
            external_image_id=external_image_id,
        )

        if not success:
            return Response(
                {"detail": message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create face profile
        face_profile, created = UserFaceProfile.objects.get_or_create(
            user=user,
            defaults={
                "rekognition_face_id": face_id,
                "collection_id": collection_id,
                "phone_number": phone_number,
            },
        )

        # If profile exists but face_id changed, delete old face from Rekognition
        if not created and face_profile.rekognition_face_id and face_profile.rekognition_face_id != face_id:
            delete_face_from_rekognition(face_profile.rekognition_face_id, collection_id)

        # Update face profile
        face_profile.rekognition_face_id = face_id
        face_profile.collection_id = collection_id
        face_profile.is_enrolled = True
        face_profile.enrolled_at = timezone.now()
        face_profile.phone_number = phone_number
        face_profile.save()

        return Response(
            {
                "detail": "Face enrolled successfully. You can now login using facial recognition.",
                "face_profile": {
                    "is_enrolled": face_profile.is_enrolled,
                    "enrolled_at": face_profile.enrolled_at,
                },
            },
            status=status.HTTP_200_OK,
        )


class FaceLoginView(APIView):
    """
    POST /api/auth/face/login/
    Login using facial recognition.
    Backward compatible: Users can still use OTP login if they prefer.
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = FaceLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        face_image = serializer.validated_data["face_image"]
        phone_number = serializer.validated_data.get("phone_number")

        # Read image bytes
        face_image.seek(0)
        image_bytes = face_image.read()

        # Search for face in Rekognition collection
        collection_id = "finmate-users"
        success, matches, message = search_face_in_rekognition(
            image_bytes=image_bytes,
            collection_id=collection_id,
            max_faces=1,
            face_match_threshold=80,  # 80% similarity threshold
        )

        if not success:
            return Response(
                {"detail": message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not matches:
            return Response(
                {"detail": "Face not recognized. Please ensure you have enrolled your face, or use OTP login."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Get the matched face
        match = matches[0]
        matched_face_id = match["face_id"]
        similarity = match["similarity"]
        external_image_id = match.get("external_image_id")  # This should be user.id

        # Find user by face_id or external_image_id
        try:
            if external_image_id:
                # Try to find user by UUID (external_image_id)
                user = User.objects.get(id=external_image_id)
            else:
                # Fallback: find by face_id in UserFaceProfile
                face_profile = UserFaceProfile.objects.get(
                    rekognition_face_id=matched_face_id,
                    is_enrolled=True,
                )
                user = face_profile.user
        except User.DoesNotExist:
            return Response(
                {"detail": "User account not found for this face."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except UserFaceProfile.DoesNotExist:
            return Response(
                {"detail": "Face profile not found. Please enroll your face first."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Optional: If phone_number provided, verify it matches
        if phone_number:
            if user.username != phone_number and user.phone != phone_number:
                return Response(
                    {"detail": "Phone number does not match the enrolled account."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Get user profile data from PersonalDemographic
        mobile_number = user.phone or user.username  # Use phone field or username (which is phone_number)
        
        # Initialize user profile fields
        full_name = None
        age = None
        gender = None
        state = None
        city_district = None
        
        # Try to get data from PersonalDemographic
        try:
            personal_demo = PersonalDemographic.objects.get(user=user)
            full_name = personal_demo.full_name
            age = personal_demo.age
            gender = personal_demo.gender
            state = personal_demo.state
            city_district = personal_demo.city_district
        except PersonalDemographic.DoesNotExist:
            # Fallback to User model fields for name only
            if user.first_name or user.last_name:
                full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

        # Get onboarding progress details
        onboarding_details = get_onboarding_progress_details(user)

        return Response(
            {
                "detail": f"Face recognized successfully (similarity: {similarity:.2f}%).",
                "access": str(access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.id),
                    "phone_number": mobile_number,
                    "full_name": full_name,
                    "age": age,
                    "gender": gender,
                    "state": state,
                    "city_district": city_district,
                },
                "onboarding": onboarding_details,
                "face_match": {
                    "similarity": similarity,
                    "face_id": matched_face_id,
                },
            },
            status=status.HTTP_200_OK,
        )
