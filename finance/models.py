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
    """
    Questions 1-10: Personal & Demographic Information
    All questions on one page
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="personal_demographic")

    # Q1: Full Name
    full_name = models.CharField(max_length=200, null=True, blank=True)
    
    # Q2: Age
    age = models.IntegerField(null=True, blank=True)
    
    # Q3: Gender
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    
    # Q4: State
    state = models.CharField(max_length=100, null=True, blank=True)
    
    # Q5: City / District
    city_district = models.CharField(max_length=100, null=True, blank=True)
    
    # Q6: Occupation Type
    OCCUPATION_CHOICES = [
        ("Gig worker", "Gig worker"),
        ("Small retailer", "Small retailer"),
        ("Farmer", "Farmer"),
        ("Other", "Other"),
    ]
    occupation_type = models.CharField(max_length=100, choices=OCCUPATION_CHOICES, null=True, blank=True)
    
    # Q7: Marital Status
    MARITAL_STATUS_CHOICES = [
        ("Married", "Married"),
        ("Single", "Single"),
        ("Other", "Other"),
    ]
    marital_status = models.CharField(max_length=50, choices=MARITAL_STATUS_CHOICES, null=True, blank=True)
    
    # Q8: Children
    CHILDREN_CHOICES = [
        ("Yes", "Yes"),
        ("No", "No"),
        ("Daughter", "Daughter"),
    ]
    children = models.CharField(max_length=50, choices=CHILDREN_CHOICES, null=True, blank=True)
    
    # Q9: Dependents
    dependents = models.IntegerField(null=True, blank=True)
    
    # Q10: Education Level
    EDUCATION_CHOICES = [
        ("None", "None"),
        ("School", "School"),
        ("College", "College"),
        ("Graduate", "Graduate"),
        ("Other", "Other"),
    ]
    education_level = models.CharField(max_length=100, choices=EDUCATION_CHOICES, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Personal Demographic - {self.user.username}"


class IncomeEmployment(models.Model):
    """
    Question 11: Income & Employment
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="income_employment")
    
    # Q11: Primary Source of Income
    primary_income_source = models.CharField(max_length=200, null=True, blank=True)  # e.g. Swiggy, Zomato, Self-employed, Farming
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Income Employment - {self.user.username}"


class IncomeStability(models.Model):
    """
    Questions 12-15: Income Stability (Subcategory A, B, C, D)
    All questions on one page
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="income_stability")
    
    # Q12 (A): Monthly income from all platforms
    MONTHLY_INCOME_CHOICES = [
        ("₹5,000–10,000", "₹5,000–10,000"),
        ("₹10,001–20,000", "₹10,001–20,000"),
        ("₹20,001–30,000", "₹20,001–30,000"),
        ("₹30,001–50,000", "₹30,001–50,000"),
        ("₹50,000+", "₹50,000+"),
    ]
    monthly_income = models.CharField(max_length=50, choices=MONTHLY_INCOME_CHOICES, null=True, blank=True)
    
    # Q13 (B): Income drop frequency in last 3 months
    INCOME_DROP_CHOICES = [
        ("Never", "Never"),
        ("Once", "Once"),
        ("Often", "Often"),
        ("Almost every month", "Almost every month"),
    ]
    income_drop_frequency = models.CharField(max_length=50, choices=INCOME_DROP_CHOICES, null=True, blank=True)
    
    # Q14 (C): Average working days per week
    WORKING_DAYS_CHOICES = [
        ("1–2 days", "1–2 days"),
        ("3–4 days", "3–4 days"),
        ("5–6 days", "5–6 days"),
        ("Every day", "Every day"),
    ]
    working_days_per_week = models.CharField(max_length=50, choices=WORKING_DAYS_CHOICES, null=True, blank=True)
    
    # Q15 (D): Income trend over past 6 months
    INCOME_TREND_CHOICES = [
        ("Increased", "Increased"),
        ("Stable", "Stable"),
        ("Decreased", "Decreased"),
    ]
    income_trend = models.CharField(max_length=50, choices=INCOME_TREND_CHOICES, null=True, blank=True)
    
    # Calculated scores (0-1)
    score_a = models.FloatField(null=True, blank=True, help_text="Q12 score")
    score_b = models.FloatField(null=True, blank=True, help_text="Q13 score")
    score_c = models.FloatField(null=True, blank=True, help_text="Q14 score")
    score_d = models.FloatField(null=True, blank=True, help_text="Q15 score")
    subcategory_score = models.FloatField(null=True, blank=True, help_text="Weighted subcategory score")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Income Stability - {self.user.username}"


class FinancialBehavior(models.Model):
    """
    Questions 16-19: Financial Behavior (Subcategory A, B, C, D)
    All questions on one page
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="financial_behavior")
    
    # Q16 (A): Monthly savings amount
    MONTHLY_SAVINGS_CHOICES = [
        ("Less than ₹500", "Less than ₹500"),
        ("₹500–₹1,000", "₹500–₹1,000"),
        ("₹1,000–₹3,000", "₹1,000–₹3,000"),
        ("More than ₹3,000", "More than ₹3,000"),
    ]
    monthly_savings = models.CharField(max_length=50, choices=MONTHLY_SAVINGS_CHOICES, null=True, blank=True)
    
    # Q17 (B): How do you usually save money (checkboxes - stored as JSON array)
    SAVING_METHOD_CHOICES = [
        ("Bank account", "Bank account"),
        ("Wallet (Paytm, GPay, etc.)", "Wallet (Paytm, GPay, etc.)"),
        ("Cash at home", "Cash at home"),
        ("Not saving currently", "Not saving currently"),
    ]
    saving_methods = models.JSONField(default=list, null=True, blank=True, help_text="Array of saving method choices")
    
    # Q18 (C): Missed EMI/loan/BNPL payments in last 3 months
    MISSED_PAYMENT_CHOICES = [
        ("Yes", "Yes"),
        ("No", "No"),
        ("Not applicable", "Not applicable"),
    ]
    missed_payments = models.CharField(max_length=50, choices=MISSED_PAYMENT_CHOICES, null=True, blank=True)
    
    # Q19 (D): Bill payment timeliness
    BILL_PAYMENT_CHOICES = [
        ("Always", "Always"),
        ("Mostly", "Mostly"),
        ("Sometimes", "Sometimes"),
        ("Rarely", "Rarely"),
    ]
    bill_payment_timeliness = models.CharField(max_length=50, choices=BILL_PAYMENT_CHOICES, null=True, blank=True)
    
    # Calculated scores (0-1)
    score_a = models.FloatField(null=True, blank=True, help_text="Q16 score")
    score_b = models.FloatField(null=True, blank=True, help_text="Q17 score")
    score_c = models.FloatField(null=True, blank=True, help_text="Q18 score")
    score_d = models.FloatField(null=True, blank=True, help_text="Q19 score")
    subcategory_score = models.FloatField(null=True, blank=True, help_text="Weighted subcategory score")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Financial Behavior - {self.user.username}"


class ReliabilityTenure(models.Model):
    """
    Questions 20-23: Reliability & Tenure (Subcategory A, B, C, D)
    All questions on one page
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="reliability_tenure")
    
    # Q20 (A): Platform tenure
    TENURE_CHOICES = [
        ("Less than 3 months", "Less than 3 months"),
        ("3–6 months", "3–6 months"),
        ("6–12 months", "6–12 months"),
        ("More than 1 year", "More than 1 year"),
    ]
    platform_tenure = models.CharField(max_length=50, choices=TENURE_CHOICES, null=True, blank=True)
    
    # Q21 (B): Days per week completing at least one order/ride/job
    ACTIVE_DAYS_CHOICES = [
        ("1–2", "1–2"),
        ("3–4", "3–4"),
        ("5–6", "5–6"),
        ("7 days", "7 days"),
    ]
    active_days_per_week = models.CharField(max_length=50, choices=ACTIVE_DAYS_CHOICES, null=True, blank=True)
    
    # Q22 (C): Cancellation frequency
    CANCELLATION_CHOICES = [
        ("Rarely", "Rarely"),
        ("Sometimes", "Sometimes"),
        ("Often", "Often"),
    ]
    cancellation_frequency = models.CharField(max_length=50, choices=CANCELLATION_CHOICES, null=True, blank=True)
    
    # Q23 (D): Customer rating (1-5 stars)
    RATING_CHOICES = [
        ("1", "1 star"),
        ("2", "2 stars"),
        ("3", "3 stars"),
        ("4", "4 stars"),
        ("5", "5 stars"),
    ]
    customer_rating = models.CharField(max_length=10, choices=RATING_CHOICES, null=True, blank=True)
    
    # Calculated scores (0-1)
    score_a = models.FloatField(null=True, blank=True, help_text="Q20 score")
    score_b = models.FloatField(null=True, blank=True, help_text="Q21 score")
    score_c = models.FloatField(null=True, blank=True, help_text="Q22 score")
    score_d = models.FloatField(null=True, blank=True, help_text="Q23 score")
    subcategory_score = models.FloatField(null=True, blank=True, help_text="Weighted subcategory score")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Reliability & Tenure - {self.user.username}"


class ProtectionReadiness(models.Model):
    """
    Questions 24-27: Protection Readiness (Subcategory A, B, C, D)
    All questions on one page
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="protection_readiness")
    
    # Q24 (A): Health insurance
    INSURANCE_CHOICES = [
        ("Yes", "Yes"),
        ("No", "No"),
        ("Not sure", "Not sure"),
    ]
    has_health_insurance = models.CharField(max_length=50, choices=INSURANCE_CHOICES, null=True, blank=True)
    
    # Q25 (B): Accident/life insurance
    has_accident_life_insurance = models.CharField(max_length=50, choices=INSURANCE_CHOICES, null=True, blank=True)
    
    # Q26 (C): Emergency expense handling (₹10,000)
    EMERGENCY_CHOICES = [
        ("Immediately", "Immediately"),
        ("Within 1 week", "Within 1 week"),
        ("Within 1 month", "Within 1 month"),
        ("Cannot manage", "Cannot manage"),
    ]
    emergency_expense_handling = models.CharField(max_length=50, choices=EMERGENCY_CHOICES, null=True, blank=True)
    
    # Q27 (D): Current savings/emergency funds
    SAVINGS_FUND_CHOICES = [
        ("₹0–500", "₹0–500"),
        ("₹501–1,000", "₹501–1,000"),
        ("₹1,001–5,000", "₹1,001–5,000"),
        ("₹5,000+", "₹5,000+"),
    ]
    current_savings_fund = models.CharField(max_length=50, choices=SAVINGS_FUND_CHOICES, null=True, blank=True)
    
    # Calculated scores (0-1)
    score_a = models.FloatField(null=True, blank=True, help_text="Q24 score")
    score_b = models.FloatField(null=True, blank=True, help_text="Q25 score")
    score_c = models.FloatField(null=True, blank=True, help_text="Q26 score")
    score_d = models.FloatField(null=True, blank=True, help_text="Q27 score")
    subcategory_score = models.FloatField(null=True, blank=True, help_text="Weighted subcategory score")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Protection Readiness - {self.user.username}"

class UserFinancialLiteracy(models.Model):
    """
    Question 28: Financial Literacy
    Based on training modules completed with quiz scores
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="financial_literacy")
    modules_completed = models.IntegerField(default=0)
    average_quiz_score = models.FloatField(default=0.0, help_text="Average quiz score (0-100)")
    literacy_score = models.FloatField(null=True, blank=True, help_text="Calculated score (0-1) based on modules and quiz scores")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Financial Literacy - {self.user.username} (Score: {self.literacy_score or 0.0})"



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
    details = models.TextField(null=True, blank=True, help_text="Detailed description of the product and its benefits")
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
    """
    Tracks onboarding progress for the new consolidated questionnaire structure.
    Each category is a single page with all questions.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    STEP_CHOICES = [
        ("personal_demographic", "Personal & Demographic (Q1-10)"),
        ("income_employment", "Income & Employment (Q11)"),
        ("income_stability", "Income Stability (Q12-15)"),
        ("financial_behavior", "Financial Behavior (Q16-19)"),
        ("reliability_tenure", "Reliability & Tenure (Q20-23)"),
        ("protection_readiness", "Protection Readiness (Q24-27)"),
        ("financial_literacy", "Financial Literacy (Q28)"),
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


class RiskRecommendation(models.Model):
    """
    Risk-based product recommendations based on user's risk profile.
    Maps risk category, risk trigger, and risk level to recommended products.
    """
    RISK_CATEGORY_CHOICES = [
        ("Income Stability", "Income Stability"),
        ("Financial Behavior", "Financial Behavior"),
        ("Reliability & Tenure", "Reliability & Tenure"),
        ("Protection Readiness", "Protection Readiness"),
    ]
    
    RISK_LEVEL_CHOICES = [
        ("🔴 High", "🔴 High"),
        ("🟠 Medium", "🟠 Medium"),
        ("🟢 Low", "🟢 Low"),
        ("High", "High"),  # Without emoji for API compatibility
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]
    
    risk_category = models.CharField(max_length=100, choices=RISK_CATEGORY_CHOICES, db_index=True)
    risk_trigger = models.CharField(max_length=500, help_text="Description of the risk trigger condition")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, db_index=True)
    recommended_instruments = models.TextField(help_text="Comma-separated list of recommended product names")
    behavioral_tag = models.CharField(max_length=200, help_text="Behavioral tag for categorization")
    intro_section = models.TextField(help_text="Introductory text to display in the app")
    order = models.PositiveIntegerField(default=0, help_text="Display order within same risk category and level")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["risk_category", "risk_level", "order"]
        indexes = [
            models.Index(fields=["risk_category", "risk_level"]),
        ]
        unique_together = [["risk_category", "risk_trigger", "risk_level"]]
    
    def __str__(self):
        return f"{self.risk_category} - {self.risk_level} - {self.risk_trigger[:50]}"
    
    def get_recommended_instruments_list(self):
        """Return recommended instruments as a list."""
        return [inst.strip() for inst in self.recommended_instruments.split(",") if inst.strip()]
