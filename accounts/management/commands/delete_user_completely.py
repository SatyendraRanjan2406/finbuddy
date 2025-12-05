"""
Django management command to completely delete a user and all related records.
Usage: python manage.py delete_user_completely <username_or_phone_or_id>
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth import get_user_model
from accounts.models import UserFaceProfile, PhoneOTP
from finance.models import (
    PersonalDemographic, IncomeEmployment, IncomeStability,
    FinancialBehavior, ReliabilityTenure, ProtectionReadiness,
    UserFinancialLiteracy, UHFSScore, ProductPurchase, UserProduct,
    UserPremiumPayment, UserNotification, OnboardingProgress
)
from training.models import UserTrainingProgress, TrainingUserAnswer
from aichat.models import ChatSession, ChatMessage, ChatAttachment
import boto3
from django.conf import settings


User = get_user_model()


class Command(BaseCommand):
    help = 'Completely delete a user and all related records from all tables'

    def add_arguments(self, parser):
        parser.add_argument(
            'identifier',
            type=str,
            help='Username, phone number, or user ID (UUID)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--skip-aws',
            action='store_true',
            help='Skip AWS Rekognition face deletion (if AWS credentials not available)',
        )

    def handle(self, *args, **options):
        identifier = options['identifier']
        dry_run = options['dry_run']
        skip_aws = options['skip_aws']

        # Find user by username, phone, or ID
        try:
            # Try UUID first
            try:
                import uuid
                user_id = uuid.UUID(identifier)
                user = User.objects.get(id=user_id)
            except (ValueError, User.DoesNotExist):
                # Try username
                try:
                    user = User.objects.get(username=identifier)
                except User.DoesNotExist:
                    # Try phone
                    user = User.objects.get(phone=identifier)
        except User.DoesNotExist:
            raise CommandError(f'User not found: {identifier}')

        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(self.style.WARNING(f'User to delete: {user.username}'))
        self.stdout.write(f'  ID: {user.id}')
        self.stdout.write(f'  Phone: {user.phone or "N/A"}')
        self.stdout.write(f'  Email: {user.email or "N/A"}')
        self.stdout.write(f'{"="*60}\n')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be deleted\n'))

        # Collect deletion statistics
        stats = {}

        try:
            with transaction.atomic():
                # 1. Delete AWS Rekognition face data (if enrolled)
                if not skip_aws:
                    self._delete_aws_face(user, dry_run, stats)
                else:
                    self.stdout.write(self.style.WARNING('Skipping AWS Rekognition deletion'))

                # 2. Delete Chat-related data
                self._delete_chat_data(user, dry_run, stats)

                # 3. Delete Training-related data
                self._delete_training_data(user, dry_run, stats)

                # 4. Delete Finance-related data
                self._delete_finance_data(user, dry_run, stats)

                # 5. Delete Account-related data
                self._delete_account_data(user, dry_run, stats)

                # 6. Finally, delete the User
                if not dry_run:
                    user.delete()
                    stats['user'] = 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted User: {user.username}'))
                else:
                    stats['user'] = 1
                    self.stdout.write(self.style.WARNING(f'Would delete User: {user.username}'))

                if dry_run:
                    # Rollback in dry-run mode
                    raise Exception("Dry run - rolling back")

        except Exception as e:
            if dry_run:
                # Expected in dry-run mode
                pass
            else:
                raise CommandError(f'Error deleting user: {str(e)}')

        # Print summary
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(self.style.SUCCESS('DELETION SUMMARY'))
        self.stdout.write(f'{"="*60}')
        for model_name, count in sorted(stats.items()):
            self.stdout.write(f'  {model_name}: {count} record(s)')
        self.stdout.write(f'{"="*60}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No data was actually deleted'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✓ User {user.username} and all related data deleted successfully!'))

    def _delete_aws_face(self, user, dry_run, stats):
        """Delete face from AWS Rekognition if enrolled"""
        try:
            face_profile = UserFaceProfile.objects.filter(user=user).first()
            if face_profile and face_profile.is_enrolled and face_profile.rekognition_face_id:
                if not dry_run:
                    try:
                        # Initialize Rekognition client
                        rekognition = boto3.client(
                            'rekognition',
                            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
                            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
                            region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'ap-south-1')
                        )
                        
                        # Delete face from collection
                        rekognition.delete_faces(
                            CollectionId=face_profile.collection_id,
                            FaceIds=[face_profile.rekognition_face_id]
                        )
                        self.stdout.write(self.style.SUCCESS(f'✓ Deleted face from AWS Rekognition'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'⚠ Could not delete from AWS Rekognition: {str(e)}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Would delete face from AWS Rekognition'))
                stats['aws_rekognition_face'] = 1
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠ Error handling AWS face: {str(e)}'))

    def _delete_chat_data(self, user, dry_run, stats):
        """Delete all chat-related data"""
        # Chat Attachments (must be deleted before messages)
        attachments = ChatAttachment.objects.filter(message__session__user=user)
        count = attachments.count()
        if count > 0:
            if not dry_run:
                attachments.delete()
            stats['chat_attachments'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} chat attachment(s)'))

        # Chat Messages
        messages = ChatMessage.objects.filter(session__user=user)
        count = messages.count()
        if count > 0:
            if not dry_run:
                messages.delete()
            stats['chat_messages'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} chat message(s)'))

        # Chat Sessions
        sessions = ChatSession.objects.filter(user=user)
        count = sessions.count()
        if count > 0:
            if not dry_run:
                sessions.delete()
            stats['chat_sessions'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} chat session(s)'))

    def _delete_training_data(self, user, dry_run, stats):
        """Delete all training-related data"""
        # Training User Answers
        answers = TrainingUserAnswer.objects.filter(user=user)
        count = answers.count()
        if count > 0:
            if not dry_run:
                answers.delete()
            stats['training_answers'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} training answer(s)'))

        # User Training Progress
        progress = UserTrainingProgress.objects.filter(user=user)
        count = progress.count()
        if count > 0:
            if not dry_run:
                progress.delete()
            stats['training_progress'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} training progress record(s)'))

    def _delete_finance_data(self, user, dry_run, stats):
        """Delete all finance-related data"""
        # Delete in order to respect foreign key constraints
        
        # 1. UserNotification (references user and user_product)
        notifications = UserNotification.objects.filter(user=user)
        count = notifications.count()
        if count > 0:
            if not dry_run:
                notifications.delete()
            stats['usernotification'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} notification(s)'))

        # 2. UserPremiumPayment (references user_product, which references user)
        # First get all user products for this user
        user_products = UserProduct.objects.filter(user=user)
        user_product_ids = list(user_products.values_list('id', flat=True))
        
        premium_payments = UserPremiumPayment.objects.filter(user_product_id__in=user_product_ids)
        count = premium_payments.count()
        if count > 0:
            if not dry_run:
                premium_payments.delete()
            stats['userpremiumpayment'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} premium payment(s)'))

        # 3. UserProduct (references user)
        count = user_products.count()
        if count > 0:
            if not dry_run:
                user_products.delete()
            stats['userproduct'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} user product(s)'))

        # 4. ProductPurchase (references user)
        purchases = ProductPurchase.objects.filter(user=user)
        count = purchases.count()
        if count > 0:
            if not dry_run:
                purchases.delete()
            stats['productpurchase'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} product purchase(s)'))

        # 5. OnboardingProgress (references user)
        progress = OnboardingProgress.objects.filter(user=user)
        count = progress.count()
        if count > 0:
            if not dry_run:
                progress.delete()
            stats['onboardingprogress'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} onboarding progress record(s)'))

        # 6. UHFSScore (references user)
        scores = UHFSScore.objects.filter(user=user)
        count = scores.count()
        if count > 0:
            if not dry_run:
                scores.delete()
            stats['uhfsscore'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} UHFS score(s)'))

        # 7. UserFinancialLiteracy (references user)
        literacy = UserFinancialLiteracy.objects.filter(user=user)
        count = literacy.count()
        if count > 0:
            if not dry_run:
                literacy.delete()
            stats['userfinancialliteracy'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} financial literacy record(s)'))

        # 8. ProtectionReadiness (references user)
        protection = ProtectionReadiness.objects.filter(user=user)
        count = protection.count()
        if count > 0:
            if not dry_run:
                protection.delete()
            stats['protectionreadiness'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} protection readiness record(s)'))

        # 9. ReliabilityTenure (references user)
        reliability = ReliabilityTenure.objects.filter(user=user)
        count = reliability.count()
        if count > 0:
            if not dry_run:
                reliability.delete()
            stats['reliabilitytenure'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} reliability & tenure record(s)'))

        # 10. FinancialBehavior (references user)
        behavior = FinancialBehavior.objects.filter(user=user)
        count = behavior.count()
        if count > 0:
            if not dry_run:
                behavior.delete()
            stats['financialbehavior'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} financial behavior record(s)'))

        # 11. IncomeStability (references user)
        income_stability = IncomeStability.objects.filter(user=user)
        count = income_stability.count()
        if count > 0:
            if not dry_run:
                income_stability.delete()
            stats['incomestability'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} income stability record(s)'))

        # 12. IncomeEmployment (references user)
        income_employment = IncomeEmployment.objects.filter(user=user)
        count = income_employment.count()
        if count > 0:
            if not dry_run:
                income_employment.delete()
            stats['incomeemployment'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} income employment record(s)'))

        # 13. PersonalDemographic (references user)
        personal = PersonalDemographic.objects.filter(user=user)
        count = personal.count()
        if count > 0:
            if not dry_run:
                personal.delete()
            stats['personaldemographic'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} personal demographic record(s)'))

    def _delete_account_data(self, user, dry_run, stats):
        """Delete account-related data"""
        # UserFaceProfile
        face_profiles = UserFaceProfile.objects.filter(user=user)
        count = face_profiles.count()
        if count > 0:
            if not dry_run:
                face_profiles.delete()
            stats['face_profiles'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} face profile(s)'))

        # PhoneOTP (optional - usually auto-expires, but delete if exists)
        otps = PhoneOTP.objects.filter(phone_number=user.phone)
        count = otps.count()
        if count > 0:
            if not dry_run:
                otps.delete()
            stats['phone_otps'] = count
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} OTP record(s)'))

