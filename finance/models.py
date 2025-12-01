from re import T
from tokenize import blank_re
from django.db import models
from accounts.models import User
from django.utils import timezone
import os


def sanitize_path_component(component):
    """Sanitize path component to be S3-safe (remove special characters)"""
    import re
    # Replace spaces and special characters with underscores, keep alphanumeric and hyphens
    sanitized = re.sub(r'[^\w\-]', '_', str(component))
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized or "unknown"


def get_id_proof_upload_path(instance, filename):
    """Generate upload path for ID proof: kyc/id_proofs/{username}/{date}/filename"""
    username = instance.user.username if instance.user else "anonymous"
    username = sanitize_path_component(username)
    date_str = timezone.now().strftime("%Y-%m-%d")
    # Sanitize filename but preserve extension
    name, ext = os.path.splitext(os.path.basename(filename))
    sanitized_name = sanitize_path_component(name)
    filename = f"{sanitized_name}{ext}" if ext else sanitized_name
    return f"kyc/id_proofs/{username}/{date_str}/{filename}"


def get_address_proof_upload_path(instance, filename):
    """Generate upload path for address proof: kyc/address_proofs/{username}/{date}/filename"""
    username = instance.user.username if instance.user else "anonymous"
    username = sanitize_path_component(username)
    date_str = timezone.now().strftime("%Y-%m-%d")
    # Sanitize filename but preserve extension
    name, ext = os.path.splitext(os.path.basename(filename))
    sanitized_name = sanitize_path_component(name)
    filename = f"{sanitized_name}{ext}" if ext else sanitized_name
    return f"kyc/address_proofs/{username}/{date_str}/{filename}"


def get_video_verification_upload_path(instance, filename):
    """Generate upload path for video verification: kyc/videos/{username}/{date}/filename"""
    username = instance.user.username if instance.user else "anonymous"
    username = sanitize_path_component(username)
    date_str = timezone.now().strftime("%Y-%m-%d")
    # Sanitize filename but preserve extension
    name, ext = os.path.splitext(os.path.basename(filename))
    sanitized_name = sanitize_path_component(name)
    filename = f"{sanitized_name}{ext}" if ext else sanitized_name
    return f"kyc/videos/{username}/{date_str}/{filename}"


class PersonalDemographic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="personal")

    full_name = models.CharField(max_length=200, null=True, blank=True)  # From Aadhaar
    age = models.IntegerField(null=True, blank=True)                     # From Aadhaar
    gender = models.CharField(max_length=20, null=True, blank=True)       # Aadhaar: Male/Female/Other
    state = models.CharField(max_length=100, null=True, blank=True)       # Aadhaar/User
    city_district = models.CharField(max_length=100, null=True, blank=True)
    occupation_type = models.CharField(max_length=100, null=True, blank=True)  # Gig/Farmer/Retailer/etc.
    marital_status = models.CharField(max_length=50, null=True, blank=True)
    children = models.CharField(max_length=50, null=True, blank=True)          # “Yes / No / Daughter”
    dependents = models.IntegerField(null=True, blank=True)
    education_level = models.CharField(max_length=100, null=True, blank=True)  # None/School/College/etc.


class IncomeEmployment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="income")

    primary_income_source = models.CharField(max_length=200, null=True, blank=True)  # Swiggy/Zomato/Farming etc.
    monthly_income_range = models.CharField(max_length=50, null=True, blank=True)    # <10k /10–20k/20–30k/>30k
    working_days_per_month = models.IntegerField(null=True, blank=True)
    income_variability = models.CharField(max_length=50, null=True, blank=True)      # Same/Fluctuates
    mode_of_payment = models.CharField(max_length=50, null=True, blank=True)         # Cash/Bank/UPI


class BankingFinancialAccess(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="banking")

    has_bank_account = models.BooleanField(default=False)
    type_of_account = models.CharField(max_length=50, null=True, blank=True)  # Savings/Current/None
    has_upi_wallet = models.BooleanField(default=False)
    avg_monthly_bank_balance = models.CharField(max_length=50, null=True, blank=True)  # Range slider
    bank_txn_per_month = models.IntegerField(null=True, blank=True)
    has_credit_card_bnpl = models.BooleanField(default=False)


class CreditLiabilities(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="credit")

    existing_loans = models.BooleanField(default=False)
    type_of_loan = models.CharField(max_length=100, null=True, blank=True) # Personal/Vehicle/Business
    monthly_emi = models.IntegerField(null=True, blank=True)
    missed_payments_6m = models.BooleanField(default=False)
    informal_borrowing = models.BooleanField(default=False)


class SavingsInsurance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="savings")

    regular_savings_habit = models.BooleanField(default=False)
    savings_amount_per_month = models.CharField(max_length=50, null=True, blank=True)  # Range dropdown
    has_insurance = models.CharField(max_length=200, null=True, blank=True)  # Multi-select: Health/Life/Accident
    type_of_insurance = models.CharField(max_length=50, null=True, blank=True) # Govt/Private
    has_pension_pf = models.BooleanField(default=False)


class ExpensesObligations(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="expenses")

    rent_per_month = models.IntegerField(null=True, blank=True)
    utilities_expense = models.IntegerField(null=True, blank=True)
    education_medical_expense = models.IntegerField(null=True, blank=True)
    avg_household_spend = models.IntegerField(null=True, blank=True)
    dependents_expense = models.IntegerField(null=True, blank=True)


class BehavioralPsychometric(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="behavior")

    set_monthly_savings_goals = models.BooleanField(default=False)
    track_expenses = models.BooleanField(default=False)
    extra_income_behaviour = models.CharField(max_length=50, null=True, blank=True)  # Save/Spend/Both
    payment_miss_frequency = models.CharField(max_length=50, null=True, blank=True)  # Never/Sometimes/Often
    digital_comfort_level = models.IntegerField(null=True, blank=True)  # 1–5 rating


class GovernmentSchemeEligibility(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="govt")

    has_aadhaar = models.BooleanField(default=False)
    has_pan = models.BooleanField(default=False)
    enrolled_in_scheme = models.BooleanField(default=False)
    scheme_names = models.CharField(max_length=300, null=True, blank=True)
    monthly_govt_benefit = models.IntegerField(null=True, blank=True)

class UserFinancialLiteracy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="financial_literacy")
    modules_completed = models.IntegerField(default=0)
    average_quiz_score = models.FloatField(default=0.0) # 0–100



class UHFSScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="uhfs")

    score = models.IntegerField(default=0)
    components = models.JSONField(default=dict, null=True, blank=True)  # Stores I, F, R, P, L values
    composite = models.FloatField(null=True, blank=True)  # Composite score
    domain_risk = models.JSONField(default=dict, null=True, blank=True)  # Risk classifications
    overall_risk = models.CharField(max_length=20, null=True, blank=True)  # Overall risk level
    last_updated = models.DateTimeField(auto_now=True)



class Product(models.Model):
    category = models.CharField( max_length=200, null = True , blank=True)
    name = models.CharField(max_length=200, null=True,blank=True)
    scheme_description = models.CharField(max_length=1000 , null=True, blank=True)
    purpose = models.CharField(max_length=1000, null=True , blank=True)
    behavioral_purpose_tag = models.CharField(max_length=150,null=True, blank=True)
    minimum_investment = models.CharField(max_length=100,null=True, blank=True)
    eligibility = models.TextField(null=True, blank=True)
    integration_type = models.CharField(max_length=255,null=True, blank=True)
    digital_verification_availability = models.CharField(max_length=120,null=True, blank=True)
    official_url = models.URLField(null=True, blank=True)
    ufhs_tag = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["behavioral_purpose_tag", "minimum_investment", "official_url"]

    def __str__(self) -> str:
        return f"{self.behavioral_purpose_tag} - {self.minimum_investment}"



class ProductPurchase(models.Model):
    STATUS_CHOICES = [
        ("INITIATED", "Initiated"),
        ("PENDING", "Pending"),
        ("OTP_VERIFIED", "OTP Verified"),
        ("KYC_IN_PROGRESS", "KYC In Progress"),
        ("IN_REVIEW", "In Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("COMPLETED", "Completed"),
        ("SUCCESS", "Success"),
        ("FAILURE", "Failure"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="purchases")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    # file fields will store S3 URLs via django storages
    # Files are organized by username and date in S3 bucket
    id_proof = models.FileField(upload_to=get_id_proof_upload_path, null=True, blank=True)
    address_proof = models.FileField(upload_to=get_address_proof_upload_path, null=True, blank=True)
    video_verification = models.FileField(upload_to=get_video_verification_upload_path, null=True, blank=True)

    # fields for OCR/extracted data
    pan_number = models.CharField(max_length=20, null=True, blank=True)
    aadhaar_number = models.CharField(max_length=16, null=True, blank=True)
    ocr_data = models.JSONField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="INITIATED")
    admin_comments = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # OTP fields:
    otp_code = models.CharField(max_length=8, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.product.name} ({self.status})"



class UserProduct(models.Model):
    STATUS_CHOICES = [
        ("INITIATED", "Initiated"),
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILURE", "Failure"),
        ("ACTIVE", "Active"),
        ("LAPSED", "Lapsed"),
        ("CANCELLED", "Cancelled"),
        ("MATURED", "Matured"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="user_products")

    policy_number = models.CharField(max_length=100, null=True, blank=True)
    purchase_date = models.DateTimeField()
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2)
    premium_frequency = models.CharField(choices=[
        ("MONTHLY", "Monthly"),
        ("QUARTERLY", "Quarterly"),
        ("HALF_YEARLY", "Half-Yearly"),
        ("YEARLY", "Yearly")
    ], max_length=20)

    next_premium_due = models.DateField()
    tenure_years = models.PositiveIntegerField(null=True, blank=True)
    maturity_date = models.DateField(null=True, blank=True)

    auto_renew = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="INITIATED")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class UserPremiumPayment(models.Model):
    PAYMENT_STATUS = [
        ("INITIATED", "Initiated"),
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILURE", "Failure"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
    ]

    user_product = models.ForeignKey(UserProduct, on_delete=models.CASCADE, related_name="premium_payments")

    premium_amount = models.DecimalField(max_digits=10, decimal_places=2)
    premium_date = models.DateField()   # due date
    paid_on = models.DateTimeField(null=True, blank=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default="INITIATED")
    transaction_id = models.CharField(max_length=200, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserNotification(models.Model):
    NOTIFICATION_TYPE = [
        ("PREMIUM_REMINDER", "Premium Reminder"),
        ("PREMIUM_OVERDUE", "Premium Overdue"),
        ("MATURITY_REMINDER", "Maturity Reminder"),
        ("KYC_REMINDER", "KYC Reminder"),
        ("GENERAL", "General Message"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    user_product = models.ForeignKey(UserProduct, null=True, blank=True, on_delete=models.CASCADE)

    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE)
    is_read = models.BooleanField(default=False)
    scheduled_for = models.DateTimeField()   # Notification send time

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)





class OnboardingProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    STEP_CHOICES = [
        ("personal_demographic", "Personal Demographic"),
        ("income_employment", "Income & Employment"),
        ("banking_financial_access", "Banking & Financial Access"),
        ("credit_liabilities", "Credit & Liabilities"),
        ("savings_insurance", "Savings & Insurance"),
        ("expenses_obligations", "Expenses & Obligations"),
        ("behavioral_psychometric", "Behavioral & Psychometric"),
        ("government_scheme_eligibility", "Government Scheme Eligibility"),
        ("user_financial_literacy", "User Financial Literacy"),
    ]
    
    # Step the user is currently answering
    current_step = models.CharField(max_length=50, choices=STEP_CHOICES, null=True, blank=True)

    # Highest step completed
    completed_step = models.CharField(max_length=50, choices=STEP_CHOICES, null=True, blank=True)

    # Easy boolean flag
    is_completed = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} onboarding progress"
