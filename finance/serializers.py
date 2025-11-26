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

from .models import ProductPurchase
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'



class ProductPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPurchase
        read_only_fields = ("status", "ocr_data", "pan_number", "aadhaar_number", "otp_verified", "created_at")
        fields = [
            "id", "product", "full_name", "email", "phone",
            "id_proof", "address_proof", "video_verification",
            "status", "pan_number", "aadhaar_number", "ocr_data", "created_at"
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



