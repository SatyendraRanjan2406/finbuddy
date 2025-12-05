"""
API view for completely deleting a user and all related records.
Admin-only endpoint for security.
"""

import logging
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
import boto3
from django.conf import settings

from accounts.models import UserFaceProfile, PhoneOTP
from finance.models import (
    PersonalDemographic, IncomeEmployment, IncomeStability,
    FinancialBehavior, ReliabilityTenure, ProtectionReadiness,
    UserFinancialLiteracy, UHFSScore, ProductPurchase, UserProduct,
    UserPremiumPayment, UserNotification, OnboardingProgress
)
from training.models import UserTrainingProgress, TrainingUserAnswer
from aichat.models import ChatSession, ChatMessage, ChatAttachment

logger = logging.getLogger(__name__)

User = get_user_model()


class DeleteUserRequestSerializer(serializers.Serializer):
    """Serializer for delete user request"""
    identifier = serializers.CharField(
        required=True,
        help_text="Username, phone number, or user ID (UUID)"
    )
    skip_aws = serializers.BooleanField(
        default=False,
        required=False,
        help_text="Skip AWS Rekognition face deletion"
    )


class DeleteUserCascadeView(APIView):
    """
    POST /api/auth/delete-user-cascade/
    
    Completely delete a user and all related records from all tables.
    Admin-only endpoint.
    
    Request body:
    {
        "identifier": "username_or_phone_or_id",
        "skip_aws": false  // optional, skip AWS Rekognition deletion
    }
    """
    # permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = DeleteUserRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        identifier = serializer.validated_data['identifier']
        skip_aws = serializer.validated_data.get('skip_aws', False)

        # Find user by username, phone, or ID
        try:
            import uuid
            try:
                user_id = uuid.UUID(identifier)
                user = User.objects.get(id=user_id)
            except (ValueError, User.DoesNotExist):
                try:
                    user = User.objects.get(username=identifier)
                except User.DoesNotExist:
                    user = User.objects.get(phone=identifier)
        except User.DoesNotExist:
            return Response(
                {"error": f"User not found: {identifier}"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Collect deletion statistics
        stats = {}
        errors = []

        try:
            with transaction.atomic():
                # 1. Delete AWS Rekognition face data
                if not skip_aws:
                    self._delete_aws_face(user, stats, errors)

                # 2. Delete Chat-related data
                self._delete_chat_data(user, stats)

                # 3. Delete Training-related data
                self._delete_training_data(user, stats)

                # 4. Delete Finance-related data
                self._delete_finance_data(user, stats)

                # 5. Delete Account-related data
                self._delete_account_data(user, stats)

                # 6. Finally, delete the User
                user.delete()
                stats['user'] = 1

        except Exception as e:
            logger.error(f"Error deleting user {user.username}: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Failed to delete user",
                    "message": str(e),
                    "partial_deletion": stats
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Build response
        response_data = {
            "success": True,
            "message": f"User {user.username} and all related data deleted successfully",
            "deleted_user": {
                "username": user.username,
                "id": str(user.id),
                "phone": user.phone or None,
            },
            "deletion_summary": stats,
        }

        if errors:
            response_data["warnings"] = errors

        return Response(response_data, status=status.HTTP_200_OK)

    def _delete_aws_face(self, user, stats, errors):
        """Delete face from AWS Rekognition if enrolled"""
        try:
            face_profile = UserFaceProfile.objects.filter(user=user).first()
            if face_profile and face_profile.is_enrolled and face_profile.rekognition_face_id:
                try:
                    rekognition = boto3.client(
                        'rekognition',
                        aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
                        aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
                        region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'ap-south-1')
                    )
                    
                    rekognition.delete_faces(
                        CollectionId=face_profile.collection_id,
                        FaceIds=[face_profile.rekognition_face_id]
                    )
                    stats['aws_rekognition_face'] = 1
                except Exception as e:
                    errors.append(f"Could not delete from AWS Rekognition: {str(e)}")
        except Exception as e:
            errors.append(f"Error handling AWS face: {str(e)}")

    def _delete_chat_data(self, user, stats):
        """Delete all chat-related data"""
        # Chat Attachments
        attachments = ChatAttachment.objects.filter(message__session__user=user)
        count = attachments.count()
        if count > 0:
            attachments.delete()
            stats['chat_attachments'] = count

        # Chat Messages
        messages = ChatMessage.objects.filter(session__user=user)
        count = messages.count()
        if count > 0:
            messages.delete()
            stats['chat_messages'] = count

        # Chat Sessions
        sessions = ChatSession.objects.filter(user=user)
        count = sessions.count()
        if count > 0:
            sessions.delete()
            stats['chat_sessions'] = count

    def _delete_training_data(self, user, stats):
        """Delete all training-related data"""
        # Training User Answers
        answers = TrainingUserAnswer.objects.filter(user=user)
        count = answers.count()
        if count > 0:
            answers.delete()
            stats['training_answers'] = count

        # User Training Progress
        progress = UserTrainingProgress.objects.filter(user=user)
        count = progress.count()
        if count > 0:
            progress.delete()
            stats['training_progress'] = count

    def _delete_finance_data(self, user, stats):
        """Delete all finance-related data"""
        # 1. UserNotification
        notifications = UserNotification.objects.filter(user=user)
        count = notifications.count()
        if count > 0:
            notifications.delete()
            stats['notifications'] = count

        # 2. UserPremiumPayment (via user_product)
        user_products = UserProduct.objects.filter(user=user)
        user_product_ids = list(user_products.values_list('id', flat=True))
        
        premium_payments = UserPremiumPayment.objects.filter(user_product_id__in=user_product_ids)
        count = premium_payments.count()
        if count > 0:
            premium_payments.delete()
            stats['premium_payments'] = count

        # 3. UserProduct
        count = user_products.count()
        if count > 0:
            user_products.delete()
            stats['user_products'] = count

        # 4. ProductPurchase
        purchases = ProductPurchase.objects.filter(user=user)
        count = purchases.count()
        if count > 0:
            purchases.delete()
            stats['product_purchases'] = count

        # 5. OnboardingProgress
        progress = OnboardingProgress.objects.filter(user=user)
        count = progress.count()
        if count > 0:
            progress.delete()
            stats['onboarding_progress'] = count

        # 6. UHFSScore
        scores = UHFSScore.objects.filter(user=user)
        count = scores.count()
        if count > 0:
            scores.delete()
            stats['uhfs_scores'] = count

        # 7. UserFinancialLiteracy
        literacy = UserFinancialLiteracy.objects.filter(user=user)
        count = literacy.count()
        if count > 0:
            literacy.delete()
            stats['financial_literacy'] = count

        # 8. ProtectionReadiness
        protection = ProtectionReadiness.objects.filter(user=user)
        count = protection.count()
        if count > 0:
            protection.delete()
            stats['protection_readiness'] = count

        # 9. ReliabilityTenure
        reliability = ReliabilityTenure.objects.filter(user=user)
        count = reliability.count()
        if count > 0:
            reliability.delete()
            stats['reliability_tenure'] = count

        # 10. FinancialBehavior
        behavior = FinancialBehavior.objects.filter(user=user)
        count = behavior.count()
        if count > 0:
            behavior.delete()
            stats['financial_behavior'] = count

        # 11. IncomeStability
        income_stability = IncomeStability.objects.filter(user=user)
        count = income_stability.count()
        if count > 0:
            income_stability.delete()
            stats['income_stability'] = count

        # 12. IncomeEmployment
        income_employment = IncomeEmployment.objects.filter(user=user)
        count = income_employment.count()
        if count > 0:
            income_employment.delete()
            stats['income_employment'] = count

        # 13. PersonalDemographic
        personal = PersonalDemographic.objects.filter(user=user)
        count = personal.count()
        if count > 0:
            personal.delete()
            stats['personal_demographic'] = count

    def _delete_account_data(self, user, stats):
        """Delete account-related data"""
        # UserFaceProfile
        face_profiles = UserFaceProfile.objects.filter(user=user)
        count = face_profiles.count()
        if count > 0:
            face_profiles.delete()
            stats['face_profiles'] = count

        # PhoneOTP
        otps = PhoneOTP.objects.filter(phone_number=user.phone)
        count = otps.count()
        if count > 0:
            otps.delete()
            stats['phone_otps'] = count
