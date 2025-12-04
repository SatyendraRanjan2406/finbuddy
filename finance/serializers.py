from rest_framework import serializers
from finance.models import (
    PersonalDemographic,
    IncomeEmployment,
    IncomeStability,
    FinancialBehavior,
    ReliabilityTenure,
    ProtectionReadiness,
    UHFSScore,
)


from rest_framework import serializers

from .models import ProductPurchase, UserProduct, UserPremiumPayment, Product, RiskRecommendation


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'



class ProductPurchaseSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_details = ProductSerializer(source="product", read_only=True)
    
    class Meta:
        model = ProductPurchase
        read_only_fields = ("status", "ocr_data", "pan_number", "aadhaar_number", "otp_verified", "created_at", "updated_at")
        fields = [
            "id", "product", "product_name", "product_details", "user", "full_name", "email", "phone",
            "id_proof", "address_proof", "video_verification",
            "status", "pan_number", "aadhaar_number", "ocr_data", 
            "otp_verified", "admin_comments", "created_at", "updated_at"
        ]

class OTPVerifySerializer(serializers.Serializer):
    application_id = serializers.IntegerField()
    otp = serializers.CharField(max_length=8)


class PersonalDemographicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDemographic
        fields = [
            "id",
            "full_name",
            "age",
            "gender",
            "state",
            "city_district",
            "occupation_type",
            "marital_status",
            "children",
            "dependents",
            "education_level",
        ]
        read_only_fields = ["id"]


class IncomeEmploymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeEmployment
        fields = [
            "id",
            "primary_income_source",
        ]
        read_only_fields = ["id"]


class IncomeStabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeStability
        fields = [
            "id",
            "monthly_income",
            "income_drop_frequency",
            "working_days_per_week",
            "income_trend",
            "score_a",
            "score_b",
            "score_c",
            "score_d",
            "subcategory_score",
        ]
        read_only_fields = ["id", "score_a", "score_b", "score_c", "score_d", "subcategory_score"]


class FinancialBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialBehavior
        fields = [
            "id",
            "monthly_savings",
            "saving_methods",
            "missed_payments",
            "bill_payment_timeliness",
            "score_a",
            "score_b",
            "score_c",
            "score_d",
            "subcategory_score",
        ]
        read_only_fields = ["id", "score_a", "score_b", "score_c", "score_d", "subcategory_score"]


class ReliabilityTenureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReliabilityTenure
        fields = [
            "id",
            "platform_tenure",
            "active_days_per_week",
            "cancellation_frequency",
            "customer_rating",
            "score_a",
            "score_b",
            "score_c",
            "score_d",
            "subcategory_score",
        ]
        read_only_fields = ["id", "score_a", "score_b", "score_c", "score_d", "subcategory_score"]


class ProtectionReadinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtectionReadiness
        fields = [
            "id",
            "has_health_insurance",
            "has_accident_life_insurance",
            "emergency_expense_handling",
            "current_savings_fund",
            "score_a",
            "score_b",
            "score_c",
            "score_d",
            "subcategory_score",
        ]
        read_only_fields = ["id", "score_a", "score_b", "score_c", "score_d", "subcategory_score"]


# OLD SERIALIZERS REMOVED - Models no longer exist
# These serializers referenced old models that have been replaced:
# - BankingFinancialAccess -> Replaced by FinancialBehavior
# - CreditLiabilities -> Replaced by FinancialBehavior
# - SavingsInsurance -> Replaced by ProtectionReadiness
# - ExpensesObligations -> Removed (not in new structure)
# - BehavioralPsychometric -> Replaced by FinancialBehavior
# - GovernmentSchemeEligibility -> Removed (not in new structure)


class UHFSScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = UHFSScore
        fields = [
            "id",
            "score",
            "last_updated",
        ]
        read_only_fields = ["id", "score", "last_updated"]



from rest_framework import serializers

class ModuleAnswerSerializer(serializers.Serializer):
    module_key = serializers.CharField()
    answer_payload = serializers.JSONField()


class UserProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_details = ProductSerializer(source="product", read_only=True)
    
    class Meta:
        model = UserProduct
        fields = '__all__'
        read_only_fields = ("created_at", "updated_at", "status")


class UserPremiumPaymentSerializer(serializers.ModelSerializer):
    user_product_details = UserProductSerializer(source="user_product", read_only=True)
    
    class Meta:
        model = UserPremiumPayment
        fields = '__all__'
        read_only_fields = ("created_at", "updated_at", "payment_status")


class ProductPurchaseDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for product purchase with related UserProduct and UserPremiumPayment"""
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_details = ProductSerializer(source="product", read_only=True)
    user_product = serializers.SerializerMethodField()
    premium_payments = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductPurchase
        fields = [
            "id", "product", "product_name", "product_details", "user", "full_name", "email", "phone",
            "id_proof", "address_proof", "video_verification",
            "status", "pan_number", "aadhaar_number", "ocr_data", 
            "otp_verified", "admin_comments", "created_at", "updated_at",
            "user_product", "premium_payments"
        ]
        read_only_fields = ("status", "ocr_data", "pan_number", "aadhaar_number", "otp_verified", "created_at", "updated_at")
    
    def get_user_product(self, obj):
        """Get related UserProduct for this purchase"""
        try:
            user_product = UserProduct.objects.filter(
                user=obj.user,
                product=obj.product,
                purchase_date__date=obj.created_at.date()
            ).first()
            if user_product:
                return UserProductSerializer(user_product).data
        except:
            pass
        return None
    
    def get_premium_payments(self, obj):
        """Get related premium payments for this purchase"""
        try:
            user_product = UserProduct.objects.filter(
                user=obj.user,
                product=obj.product,
                purchase_date__date=obj.created_at.date()
            ).first()
            if user_product:
                payments = UserPremiumPayment.objects.filter(user_product=user_product).order_by('-premium_date')
                return UserPremiumPaymentSerializer(payments, many=True).data
        except:
            pass
        return []


class ProductPurchaseInitiateSerializer(serializers.Serializer):
    """Serializer for initiating product purchase"""
    product_id = serializers.IntegerField(help_text="ID of the product to purchase")
    premium_amount = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Premium amount per payment")
    premium_frequency = serializers.ChoiceField(choices=[
        ("MONTHLY", "Monthly"),
        ("QUARTERLY", "Quarterly"),
        ("HALF_YEARLY", "Half-Yearly"),
        ("YEARLY", "Yearly")
    ], help_text="Frequency of premium payments")
    tenure_years = serializers.IntegerField(required=False, allow_null=True, help_text="Tenure in years (optional)")
    auto_renew = serializers.BooleanField(default=True, help_text="Auto-renewal setting (default: true)")
    policy_number = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True, help_text="Policy number if available (optional)")
    maturity_date = serializers.DateField(required=False, allow_null=True, help_text="Maturity date (optional, will be calculated from tenure_years if not provided)")
    next_premium_due = serializers.DateField(required=False, allow_null=True, help_text="Next premium due date (optional, will be calculated from premium_frequency if not provided)")
    
    # KYC File fields (all optional)
    id_proof = serializers.FileField(required=False, allow_null=True, help_text="ID proof document (Aadhaar/PAN/Driving License)")
    address_proof = serializers.FileField(required=False, allow_null=True, help_text="Address proof document (optional)")
    video_verification = serializers.FileField(required=False, allow_null=True, help_text="Video verification file (optional)")
    
    # Additional user information (optional, will use authenticated user if not provided)
    full_name = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True, help_text="Full name (optional, uses authenticated user if not provided)")
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True, help_text="Email (optional, uses authenticated user if not provided)")
    phone = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True, help_text="Phone number (optional, uses authenticated user if not provided)")


class RiskRecommendationRequestSerializer(serializers.Serializer):
    """Serializer for risk recommendation API request."""
    risk = serializers.ChoiceField(
        choices=RiskRecommendation.RISK_CATEGORY_CHOICES,
        help_text="Risk category: Income Stability, Financial Behavior, Reliability & Tenure, or Protection Readiness"
    )
    risk_level = serializers.ChoiceField(
        choices=[
            ("High", "High"),
            ("Medium", "Medium"),
            ("Low", "Low"),
            ("🔴 High", "🔴 High"),
            ("🟠 Medium", "🟠 Medium"),
            ("🟢 Low", "🟢 Low"),
        ],
        help_text="Risk level: High, Medium, or Low (with or without emoji)"
    )


class RiskRecommendationResponseSerializer(serializers.ModelSerializer):
    """Serializer for risk recommendation API response."""
    recommended_instruments = serializers.SerializerMethodField()
    
    class Meta:
        model = RiskRecommendation
        fields = [
            "id",
            "risk_category",
            "risk_trigger",
            "risk_level",
            "recommended_instruments",
            "behavioral_tag",
            "intro_section",
        ]
    
    def get_recommended_instruments(self, obj):
        """Return recommended instruments as a list."""
        return obj.get_recommended_instruments_list()


