from django.contrib import admin

from finance.models import (
    BehavioralPsychometric,
    BankingFinancialAccess,
    CreditLiabilities,
    ExpensesObligations,
    GovernmentSchemeEligibility,
    IncomeEmployment,
    PersonalDemographic,
    Product,
    SavingsInsurance,
    UHFSScore,
    UserFinancialLiteracy,
)


@admin.register(PersonalDemographic)
class PersonalDemographicAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "age", "gender", "state", "city_district", "occupation_type")
    search_fields = ("full_name", "user__username", "state", "city_district", "occupation_type")
    list_filter = ("gender", "state", "occupation_type", "marital_status", "education_level")
    raw_id_fields = ("user",)


@admin.register(IncomeEmployment)
class IncomeEmploymentAdmin(admin.ModelAdmin):
    list_display = ("user", "primary_income_source", "monthly_income_range", "working_days_per_month", "income_variability")
    search_fields = ("user__username", "primary_income_source", "monthly_income_range")
    list_filter = ("monthly_income_range", "income_variability", "mode_of_payment")
    raw_id_fields = ("user",)


@admin.register(BankingFinancialAccess)
class BankingFinancialAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "has_bank_account", "type_of_account", "has_upi_wallet", "has_credit_card_bnpl")
    search_fields = ("user__username", "type_of_account")
    list_filter = ("has_bank_account", "has_upi_wallet", "has_credit_card_bnpl", "type_of_account")
    raw_id_fields = ("user",)


@admin.register(CreditLiabilities)
class CreditLiabilitiesAdmin(admin.ModelAdmin):
    list_display = ("user", "existing_loans", "type_of_loan", "monthly_emi", "missed_payments_6m", "informal_borrowing")
    search_fields = ("user__username", "type_of_loan")
    list_filter = ("existing_loans", "missed_payments_6m", "informal_borrowing", "type_of_loan")
    raw_id_fields = ("user",)


@admin.register(SavingsInsurance)
class SavingsInsuranceAdmin(admin.ModelAdmin):
    list_display = ("user", "regular_savings_habit", "savings_amount_per_month", "has_insurance", "has_pension_pf")
    search_fields = ("user__username", "type_of_insurance", "has_insurance")
    list_filter = ("regular_savings_habit", "has_insurance", "has_pension_pf", "type_of_insurance")
    raw_id_fields = ("user",)


@admin.register(ExpensesObligations)
class ExpensesObligationsAdmin(admin.ModelAdmin):
    list_display = ("user", "rent_per_month", "utilities_expense", "avg_household_spend", "dependents_expense")
    search_fields = ("user__username",)
    list_filter = ()
    raw_id_fields = ("user",)


@admin.register(BehavioralPsychometric)
class BehavioralPsychometricAdmin(admin.ModelAdmin):
    list_display = ("user", "set_monthly_savings_goals", "track_expenses", "extra_income_behaviour", "digital_comfort_level")
    search_fields = ("user__username", "extra_income_behaviour", "payment_miss_frequency")
    list_filter = ("set_monthly_savings_goals", "track_expenses", "extra_income_behaviour", "payment_miss_frequency")
    raw_id_fields = ("user",)


@admin.register(GovernmentSchemeEligibility)
class GovernmentSchemeEligibilityAdmin(admin.ModelAdmin):
    list_display = ("user", "has_aadhaar", "has_pan", "enrolled_in_scheme", "monthly_govt_benefit")
    search_fields = ("user__username", "scheme_names")
    list_filter = ("has_aadhaar", "has_pan", "enrolled_in_scheme")
    raw_id_fields = ("user",)


@admin.register(UserFinancialLiteracy)
class UserFinancialLiteracyAdmin(admin.ModelAdmin):
    list_display = ("user", "modules_completed", "average_quiz_score")
    search_fields = ("user__username",)
    list_filter = ("modules_completed",)
    raw_id_fields = ("user",)


@admin.register(UHFSScore)
class UHFSScoreAdmin(admin.ModelAdmin):
    list_display = ("user", "score", "last_updated")
    search_fields = ("user__username",)
    list_filter = ("last_updated",)
    raw_id_fields = ("user",)
    readonly_fields = ("last_updated",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "behavioral_purpose_tag",
        "minimum_investment",
        "integration_type",
        "digital_verification_availability",
        "ufhs_tag",
        "created_at",
    )
    search_fields = (
        "behavioral_purpose_tag",
        "eligibility",
        "integration_type",
        "official_url",
    )
    list_filter = ("behavioral_purpose_tag", "digital_verification_availability", "ufhs_tag", "created_at")
    readonly_fields = ("created_at", "updated_at")
