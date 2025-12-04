from django.contrib import admin

from finance.models import (
    IncomeEmployment,
    IncomeStability,
    FinancialBehavior,
    ReliabilityTenure,
    ProtectionReadiness,
    PersonalDemographic,
    Product,
    UHFSScore,
    UserFinancialLiteracy,
    ProductPurchase,
    UserProduct,
    UserPremiumPayment,
    UserNotification,
)


@admin.register(PersonalDemographic)
class PersonalDemographicAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "age", "gender", "state", "city_district", "occupation_type")
    search_fields = ("full_name", "user__username", "state", "city_district", "occupation_type")
    list_filter = ("gender", "state", "occupation_type", "marital_status", "education_level")
    raw_id_fields = ("user",)


@admin.register(IncomeEmployment)
class IncomeEmploymentAdmin(admin.ModelAdmin):
    list_display = ("user", "primary_income_source", "created_at", "updated_at")
    search_fields = ("user__username", "primary_income_source")
    list_filter = ("created_at", "updated_at")
    raw_id_fields = ("user",)


@admin.register(IncomeStability)
class IncomeStabilityAdmin(admin.ModelAdmin):
    list_display = ("user", "monthly_income", "income_drop_frequency", "working_days_per_week", "income_trend", "subcategory_score")
    search_fields = ("user__username",)
    list_filter = ("monthly_income", "income_drop_frequency", "income_trend")
    raw_id_fields = ("user",)
    readonly_fields = ("score_a", "score_b", "score_c", "score_d", "subcategory_score")


@admin.register(FinancialBehavior)
class FinancialBehaviorAdmin(admin.ModelAdmin):
    list_display = ("user", "monthly_savings", "missed_payments", "bill_payment_timeliness", "subcategory_score")
    search_fields = ("user__username",)
    list_filter = ("monthly_savings", "missed_payments", "bill_payment_timeliness")
    raw_id_fields = ("user",)
    readonly_fields = ("score_a", "score_b", "score_c", "score_d", "subcategory_score")


@admin.register(ReliabilityTenure)
class ReliabilityTenureAdmin(admin.ModelAdmin):
    list_display = ("user", "platform_tenure", "active_days_per_week", "cancellation_frequency", "customer_rating", "subcategory_score")
    search_fields = ("user__username",)
    list_filter = ("platform_tenure", "cancellation_frequency", "customer_rating")
    raw_id_fields = ("user",)
    readonly_fields = ("score_a", "score_b", "score_c", "score_d", "subcategory_score")


@admin.register(ProtectionReadiness)
class ProtectionReadinessAdmin(admin.ModelAdmin):
    list_display = ("user", "has_health_insurance", "has_accident_life_insurance", "emergency_expense_handling", "current_savings_fund", "subcategory_score")
    search_fields = ("user__username",)
    list_filter = ("has_health_insurance", "has_accident_life_insurance", "emergency_expense_handling")
    raw_id_fields = ("user",)
    readonly_fields = ("score_a", "score_b", "score_c", "score_d", "subcategory_score")


@admin.register(UserFinancialLiteracy)
class UserFinancialLiteracyAdmin(admin.ModelAdmin):
    list_display = ("user", "modules_completed", "average_quiz_score", "literacy_score")
    search_fields = ("user__username",)
    list_filter = ("modules_completed",)
    raw_id_fields = ("user",)
    readonly_fields = ("literacy_score",)


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


@admin.register(ProductPurchase)
class ProductPurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "full_name",
        "email",
        "phone",
        "status",
        "otp_verified",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "full_name",
        "email",
        "phone",
        "user__username",
        "product__name",
        "pan_number",
        "aadhaar_number",
    )
    list_filter = (
        "status",
        "otp_verified",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "otp_created_at",
        "ocr_data",
    )
    raw_id_fields = ("user", "product")
    date_hierarchy = "created_at"


@admin.register(UserProduct)
class UserProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "policy_number",
        "status",
        "premium_amount",
        "premium_frequency",
        "purchase_date",
        "next_premium_due",
        "maturity_date",
        "auto_renew",
    )
    search_fields = (
        "user__username",
        "product__name",
        "policy_number",
    )
    list_filter = (
        "status",
        "premium_frequency",
        "auto_renew",
        "purchase_date",
        "next_premium_due",
    )
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user", "product")
    date_hierarchy = "purchase_date"


@admin.register(UserPremiumPayment)
class UserPremiumPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_product",
        "premium_amount",
        "premium_date",
        "payment_status",
        "paid_on",
        "transaction_id",
        "created_at",
    )
    search_fields = (
        "user_product__user__username",
        "user_product__product__name",
        "transaction_id",
    )
    list_filter = (
        "payment_status",
        "premium_date",
        "paid_on",
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user_product",)
    date_hierarchy = "premium_date"


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "user_product",
        "notification_type",
        "is_read",
        "scheduled_for",
        "created_at",
    )
    search_fields = (
        "user__username",
        "message",
        "notification_type",
    )
    list_filter = (
        "notification_type",
        "is_read",
        "scheduled_for",
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user", "user_product")
    date_hierarchy = "scheduled_for"
