from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

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
from finance.serializers import (
    PersonalDemographicSerializer,
    IncomeEmploymentSerializer,
    BankingFinancialAccessSerializer,
    CreditLiabilitiesSerializer,
    SavingsInsuranceSerializer,
    ExpensesObligationsSerializer,
    BehavioralPsychometricSerializer,
    GovernmentSchemeEligibilitySerializer,
    UHFSScoreSerializer,
)
from finance.services.products_util import get_suggested_products_util
from finance.services.uhfs import calculate_and_store_uhfs
from finance.utils import update_progress

from .models import Product
from .serializers import ProductSerializer
from .pagination import ProductPagination


MODULE_STEP_MAP = {
    "personal_demographic": 1,
    "income_employment": 2,
    "banking_financial_access": 3,
    "credit_liabilities": 4,
    "savings_insurance": 5,
    "expenses_obligations": 6,
    "behavioral_psychometric": 7,
    "government_scheme_eligibility": 8,
    "user_financial_literacy": 9
}

TOTAL_STEPS = 9

class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all().order_by("id")

        paginator = ProductPagination()
        paginated_products = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProductByNameView(APIView):
    def get(self, request, name):
        products = Product.objects.filter(name__iexact=name).order_by("id")

        if not products.exists():
            return Response(
                {"message": "No product found with that name"},
                status=status.HTTP_404_NOT_FOUND
            )

        paginator = ProductPagination()
        paginated_products = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProductDetailView(APIView):
    """
    GET /api/finance/products/<id>/ - Get single product details by ID
    """
    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )



class PersonalDemographicView(APIView):
    """
    GET /api/finance/personal-demographic/ - Get personal demographic info
    POST /api/finance/personal-demographic/ - Create or update personal demographic info
    PUT /api/finance/personal-demographic/ - Update personal demographic info
    PATCH /api/finance/personal-demographic/ - Partial update personal demographic info
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            personal = PersonalDemographic.objects.get(user=request.user)
            serializer = PersonalDemographicSerializer(personal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PersonalDemographic.DoesNotExist:
            return Response(
                {"detail": "Personal demographic information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            personal = PersonalDemographic.objects.get(user=request.user)
            serializer = PersonalDemographicSerializer(personal, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            update_progress(request.user , "personal_demographic" )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PersonalDemographic.DoesNotExist:
            serializer = PersonalDemographicSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial=False):
        try:
            personal = PersonalDemographic.objects.get(user=request.user)
            serializer = PersonalDemographicSerializer(personal, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PersonalDemographic.DoesNotExist:
            return Response(
                {"detail": "Personal demographic information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND,
            )


class IncomeEmploymentView(APIView):
    """
    GET /api/finance/income-employment/ - Get income employment info
    POST /api/finance/income-employment/ - Create or update income employment info
    PUT /api/finance/income-employment/ - Update income employment info
    PATCH /api/finance/income-employment/ - Partial update income employment info
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            income = IncomeEmployment.objects.get(user=request.user)
            serializer = IncomeEmploymentSerializer(income)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except IncomeEmployment.DoesNotExist:
            return Response(
                {"detail": "Income employment information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            income = IncomeEmployment.objects.get(user=request.user)
            serializer = IncomeEmploymentSerializer(income, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            update_progress(request.user , "income_employment" )

            return Response(serializer.data, status=status.HTTP_200_OK)
        except IncomeEmployment.DoesNotExist:
            serializer = IncomeEmploymentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial=False):
        try:
            income = IncomeEmployment.objects.get(user=request.user)
            serializer = IncomeEmploymentSerializer(income, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except IncomeEmployment.DoesNotExist:
            return Response(
                {"detail": "Income employment information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND,
            )


class BankingFinancialAccessView(APIView):
    """
    GET /api/finance/banking-access/ - Get banking financial access info
    POST /api/finance/banking-access/ - Create or update banking financial access info
    PUT /api/finance/banking-access/ - Update banking financial access info
    PATCH /api/finance/banking-access/ - Partial update banking financial access info
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            banking = BankingFinancialAccess.objects.get(user=request.user)
            serializer = BankingFinancialAccessSerializer(banking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BankingFinancialAccess.DoesNotExist:
            return Response(
                {"detail": "Banking financial access information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            banking = BankingFinancialAccess.objects.get(user=request.user)
            serializer = BankingFinancialAccessSerializer(banking, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            update_progress(request.user , "banking_financial_access" )

            return Response(serializer.data, status=status.HTTP_200_OK)
        except BankingFinancialAccess.DoesNotExist:
            serializer = BankingFinancialAccessSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial=False):
        try:
            banking = BankingFinancialAccess.objects.get(user=request.user)
            serializer = BankingFinancialAccessSerializer(banking, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BankingFinancialAccess.DoesNotExist:
            return Response(
                {"detail": "Banking financial access information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND,
            )


class CreditLiabilitiesView(APIView):
    """
    GET /api/finance/credit-liabilities/ - Get credit liabilities info
    POST /api/finance/credit-liabilities/ - Create or update credit liabilities info
    PUT /api/finance/credit-liabilities/ - Update credit liabilities info
    PATCH /api/finance/credit-liabilities/ - Partial update credit liabilities info
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            credit = CreditLiabilities.objects.get(user=request.user)
            serializer = CreditLiabilitiesSerializer(credit)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CreditLiabilities.DoesNotExist:
            return Response(
                {"detail": "Credit liabilities information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            credit = CreditLiabilities.objects.get(user=request.user)
            serializer = CreditLiabilitiesSerializer(credit, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            update_progress(request.user , "credit_liabilities" )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CreditLiabilities.DoesNotExist:
            serializer = CreditLiabilitiesSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial=False):
        try:
            credit = CreditLiabilities.objects.get(user=request.user)
            serializer = CreditLiabilitiesSerializer(credit, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CreditLiabilities.DoesNotExist:
            return Response(
                {"detail": "Credit liabilities information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND,
            )


class SavingsInsuranceView(APIView):
    """
    GET /api/finance/savings-insurance/ - Get savings insurance info
    POST /api/finance/savings-insurance/ - Create or update savings insurance info
    PUT /api/finance/savings-insurance/ - Update savings insurance info
    PATCH /api/finance/savings-insurance/ - Partial update savings insurance info
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            savings = SavingsInsurance.objects.get(user=request.user)
            serializer = SavingsInsuranceSerializer(savings)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SavingsInsurance.DoesNotExist:
            return Response(
                {"detail": "Savings insurance information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            savings = SavingsInsurance.objects.get(user=request.user)
            serializer = SavingsInsuranceSerializer(savings, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            update_progress(request.user , "savings_insurance" )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SavingsInsurance.DoesNotExist:
            serializer = SavingsInsuranceSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial=False):
        try:
            savings = SavingsInsurance.objects.get(user=request.user)
            serializer = SavingsInsuranceSerializer(savings, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SavingsInsurance.DoesNotExist:
            return Response(
                {"detail": "Savings insurance information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ExpensesObligationsView(APIView):
    """
    GET /api/finance/expenses-obligations/ - Get expenses obligations info
    POST /api/finance/expenses-obligations/ - Create or update expenses obligations info
    PUT /api/finance/expenses-obligations/ - Update expenses obligations info
    PATCH /api/finance/expenses-obligations/ - Partial update expenses obligations info
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            expenses = ExpensesObligations.objects.get(user=request.user)
            serializer = ExpensesObligationsSerializer(expenses)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ExpensesObligations.DoesNotExist:
            return Response(
                {"detail": "Expenses obligations information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            expenses = ExpensesObligations.objects.get(user=request.user)
            serializer = ExpensesObligationsSerializer(expenses, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            update_progress(request.user , "expenses_obligations" )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ExpensesObligations.DoesNotExist:
            serializer = ExpensesObligationsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial=False):
        try:
            expenses = ExpensesObligations.objects.get(user=request.user)
            serializer = ExpensesObligationsSerializer(expenses, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ExpensesObligations.DoesNotExist:
            return Response(
                {"detail": "Expenses obligations information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND,
            )


class BehavioralPsychometricView(APIView):
    """
    GET /api/finance/behavioral-psychometric/ - Get behavioral psychometric info
    POST /api/finance/behavioral-psychometric/ - Create or update behavioral psychometric info
    PUT /api/finance/behavioral-psychometric/ - Update behavioral psychometric info
    PATCH /api/finance/behavioral-psychometric/ - Partial update behavioral psychometric info
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            behavior = BehavioralPsychometric.objects.get(user=request.user)
            serializer = BehavioralPsychometricSerializer(behavior)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BehavioralPsychometric.DoesNotExist:
            return Response(
                {"detail": "Behavioral psychometric information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            behavior = BehavioralPsychometric.objects.get(user=request.user)
            serializer = BehavioralPsychometricSerializer(behavior, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            update_progress(request.user , "behavioral_psychometric" )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BehavioralPsychometric.DoesNotExist:
            serializer = BehavioralPsychometricSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial=False):
        try:
            behavior = BehavioralPsychometric.objects.get(user=request.user)
            serializer = BehavioralPsychometricSerializer(behavior, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BehavioralPsychometric.DoesNotExist:
            return Response(
                {"detail": "Behavioral psychometric information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND,
            )


class GovernmentSchemeEligibilityView(APIView):
    """
    GET /api/finance/government-scheme/ - Get government scheme eligibility info
    POST /api/finance/government-scheme/ - Create or update government scheme eligibility info
    PUT /api/finance/government-scheme/ - Update government scheme eligibility info
    PATCH /api/finance/government-scheme/ - Partial update government scheme eligibility info
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            govt = GovernmentSchemeEligibility.objects.get(user=request.user)
            serializer = GovernmentSchemeEligibilitySerializer(govt)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except GovernmentSchemeEligibility.DoesNotExist:
            return Response(
                {"detail": "Government scheme eligibility information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            govt = GovernmentSchemeEligibility.objects.get(user=request.user)
            serializer = GovernmentSchemeEligibilitySerializer(govt, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            update_progress(request.user , "government_scheme_eligibility" )

            return Response(serializer.data, status=status.HTTP_200_OK)
        except GovernmentSchemeEligibility.DoesNotExist:
            serializer = GovernmentSchemeEligibilitySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial=False):
        try:
            govt = GovernmentSchemeEligibility.objects.get(user=request.user)
            serializer = GovernmentSchemeEligibilitySerializer(govt, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except GovernmentSchemeEligibility.DoesNotExist:
            return Response(
                {"detail": "Government scheme eligibility information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND,
            )


class UHFSScoreView(APIView):
    """
    GET /api/finance/uhfs-score/ - Get current UHFS score
    POST /api/finance/uhfs-score/ - Calculate and update UHFS score
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            uhfs = UHFSScore.objects.get(user=request.user)
            # Return same format as POST response
            result = {
                "user_id": str(request.user.id),
                "components": uhfs.components or {},
                "weights": {"I": 0.25, "F": 0.25, "R": 0.15, "P": 0.20, "L": 0.15},
                "composite": float(uhfs.composite) if uhfs.composite else 0.0,
                "uhfs_score": uhfs.score,
                "domain_risk": uhfs.domain_risk or {},
                "overall_risk": uhfs.overall_risk or "Unknown",
                "last_updated": uhfs.last_updated.isoformat() if uhfs.last_updated else None,
            }
            return Response(result, status=status.HTTP_200_OK)
        except UHFSScore.DoesNotExist:
            return Response(
                {"detail": "UHFS score not calculated yet. Use POST to calculate."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        """
        Calculate and store UHFS score based on user's financial data.
        Returns detailed breakdown of the calculation.
        """
        try:
            result = calculate_and_store_uhfs(request.user)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": f"Error calculating UHFS score: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )




@api_view(["POST"])
def get_suggested_products(request):
    ufhs_score = request.data.get("ufhs_score")
    if ufhs_score is None:
        return Response(error="UFHS Score is required" , status = 400)
    products = get_suggested_products_util(ufhs_score)
    serializer = ProductSerializer(products, many=True)
    return Response({ "products": serializer.data }, status=200)


@api_view(["POST"])
def populate_products(request):
    """Wrapper for populate function to handle missing dependencies gracefully"""
    try:
        from finance.script import populate
        return populate(request)
    except ImportError as e:
        return Response(
            {"error": f"Required dependencies not installed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


