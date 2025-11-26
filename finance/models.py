from re import T
from tokenize import blank_re
from django.db import models
from accounts.models import User

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
    last_updated = models.DateTimeField(auto_now=True)



class Product(models.Model):
    category = models.CharField( max_length=200, null = True , blank=True)
    name = models.CharField(max_length=200, null=True,blank=True)
    scheme_description = models.CharField(max_length=1000 , null=True, blank=True)
    purpose = models.CharField(max_length=1000, null=True , blank=True)
    behavioral_purpose_tag = models.CharField(max_length=150)
    minimum_investment = models.CharField(max_length=100)
    eligibility = models.TextField()
    integration_type = models.CharField(max_length=255)
    digital_verification_availability = models.CharField(max_length=120)
    official_url = models.URLField()
    ufhs_tag = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["behavioral_purpose_tag", "minimum_investment", "official_url"]

    def __str__(self) -> str:
        return f"{self.behavioral_purpose_tag} - {self.minimum_investment}"



class ProductPurchase(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("OTP_VERIFIED", "OTP Verified"),
        ("KYC_IN_PROGRESS", "KYC In Progress"),
        ("IN_REVIEW", "In Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("COMPLETED", "Completed"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="purchases")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    # file fields will store S3 URLs via django storages
    id_proof = models.FileField(upload_to="kyc/id_proofs/")
    address_proof = models.FileField(upload_to="kyc/address_proofs/", null=True, blank=True)
    video_verification = models.FileField(upload_to="kyc/videos/")

    # fields for OCR/extracted data
    pan_number = models.CharField(max_length=20, null=True, blank=True)
    aadhaar_number = models.CharField(max_length=16, null=True, blank=True)
    ocr_data = models.JSONField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    admin_comments = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # OTP fields:
    otp_code = models.CharField(max_length=8, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.product.name} ({self.status})"