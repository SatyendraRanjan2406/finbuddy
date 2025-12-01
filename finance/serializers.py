from rest_framework import serializers
from finance.models import (
    PersonalDemographic,
    IncomeEmployment,
    BankingFinancialAccess,
    CreditLiabilities,
    SavingsInsurance,
    ExpensesObligations,
    BehavioralPsychometric,
    GovernmentSchemeEligibility,
    UHFSScore,
)


from rest_framework import serializers

from .models import ProductPurchase, UserProduct, UserPremiumPayment, Product


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
            "monthly_income_range",
            "working_days_per_month",
            "income_variability",
            "mode_of_payment",
        ]
        read_only_fields = ["id"]


class BankingFinancialAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankingFinancialAccess
        fields = [
            "id",
            "has_bank_account",
            "type_of_account",
            "has_upi_wallet",
            "avg_monthly_bank_balance",
            "bank_txn_per_month",
            "has_credit_card_bnpl",
        ]
        read_only_fields = ["id"]


class CreditLiabilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditLiabilities
        fields = [
            "id",
            "existing_loans",
            "type_of_loan",
            "monthly_emi",
            "missed_payments_6m",
            "informal_borrowing",
        ]
        read_only_fields = ["id"]


class SavingsInsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsInsurance
        fields = [
            "id",
            "regular_savings_habit",
            "savings_amount_per_month",
            "has_insurance",
            "type_of_insurance",
            "has_pension_pf",
        ]
        read_only_fields = ["id"]


class ExpensesObligationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpensesObligations
        fields = [
            "id",
            "rent_per_month",
            "utilities_expense",
            "education_medical_expense",
            "avg_household_spend",
            "dependents_expense",
        ]
        read_only_fields = ["id"]


class BehavioralPsychometricSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehavioralPsychometric
        fields = [
            "id",
            "set_monthly_savings_goals",
            "track_expenses",
            "extra_income_behaviour",
            "payment_miss_frequency",
            "digital_comfort_level",
        ]
        read_only_fields = ["id"]


class GovernmentSchemeEligibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernmentSchemeEligibility
        fields = [
            "id",
            "has_aadhaar",
            "has_pan",
            "enrolled_in_scheme",
            "scheme_names",
            "monthly_govt_benefit",
        ]
        read_only_fields = ["id"]


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


