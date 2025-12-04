from django.urls import path
from finance.views import (
    PersonalDemographicView,
    IncomeEmploymentView,
    BankingFinancialAccessView,
    CreditLiabilitiesView,
    ProductByNameView,
    ProductListView,
    ProductDetailView,
    SavingsInsuranceView,
    ExpensesObligationsView,
    BehavioralPsychometricView,
    GovernmentSchemeEligibilityView,
    UHFSScoreView,
    get_suggested_products,
    populate_products,
    RiskRecommendationView,
    DashboardView,
)

from .search_views import (
    ProductSearchByCategoryName,
    ProductAdvancedSearch,
    ProductFuzzySearch,
    ProductSuggestion,
)

from .purchase_views import (
    apply_for_product, verify_otp, application_status,
    admin_approve, partner_webhook,
    initiate_product_purchase, complete_product_purchase,
    get_user_purchases, get_user_purchase_detail
)


urlpatterns = [
    path("personal-demographic/", PersonalDemographicView.as_view(), name="personal-demographic"),
    path("income-employment/", IncomeEmploymentView.as_view(), name="income-employment"),
    path("banking-access/", BankingFinancialAccessView.as_view(), name="banking-access"),
    path("credit-liabilities/", CreditLiabilitiesView.as_view(), name="credit-liabilities"),
    path("savings-insurance/", SavingsInsuranceView.as_view(), name="savings-insurance"),
    path("expenses-obligations/", ExpensesObligationsView.as_view(), name="expenses-obligations"),
    path("behavioral-psychometric/", BehavioralPsychometricView.as_view(), name="behavioral-psychometric"),
    path("government-scheme/", GovernmentSchemeEligibilityView.as_view(), name="government-scheme"),
    path("uhfs-score/", UHFSScoreView.as_view(), name="uhfs-score"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:id>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/by-name/<str:name>/", ProductByNameView.as_view(), name="product-by-name"),

    # Search Views
    path("products/search/", ProductSearchByCategoryName.as_view()),
    path("products/advanced-search/", ProductAdvancedSearch.as_view()),
    path("products/fuzzy/", ProductFuzzySearch.as_view()),
    path("products/suggest/", ProductSuggestion.as_view()),

    path("products/suggested/", get_suggested_products),

    path("populate/" , populate_products),
    
    # Risk-based recommendations
    path("risk-recommendation/", RiskRecommendationView.as_view(), name="risk-recommendation"),

    path("apply/", apply_for_product),
    path("apply/verify-otp/", verify_otp),
    path("applications/<int:application_id>/status/", application_status),
    path("applications/<int:application_id>/admin-action/", admin_approve),
    path("partner/webhook/", partner_webhook),
    
    # Product purchase endpoints
    path("purchase/", get_user_purchases, name="get-user-purchases"),
    path("purchase/initiate/", initiate_product_purchase, name="initiate-product-purchase"),
    path("purchase/<int:purchase_id>/", get_user_purchase_detail, name="get-user-purchase-detail"),
    path("purchase/<int:purchase_id>/complete/", complete_product_purchase, name="complete-product-purchase"),
]

