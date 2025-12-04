from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from finance.models import (
    PersonalDemographic,
    IncomeEmployment,
    IncomeStability,
    FinancialBehavior,
    ReliabilityTenure,
    ProtectionReadiness,
    UHFSScore,
    RiskRecommendation,
)
from accounts.models import User
from finance.serializers import (
    PersonalDemographicSerializer,
    IncomeEmploymentSerializer,
    IncomeStabilitySerializer,
    FinancialBehaviorSerializer,
    ReliabilityTenureSerializer,
    ProtectionReadinessSerializer,
    UHFSScoreSerializer,
    RiskRecommendationRequestSerializer,
    RiskRecommendationResponseSerializer,
)
from finance.services.products_util import get_suggested_products_util
from finance.services.uhfs_v2 import calculate_and_store_uhfs
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
    GET /api/finance/income-employment/ - Get income employment info (Q11)
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
            update_progress(request.user, "income_employment")

            return Response(serializer.data, status=status.HTTP_200_OK)
        except IncomeEmployment.DoesNotExist:
            serializer = IncomeEmploymentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            update_progress(request.user, "income_employment")
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


class IncomeStabilityView(APIView):
    """
    GET /api/finance/income-stability/ - Get income stability info (Q12-15)
    POST /api/finance/income-stability/ - Create or update income stability info
    All questions on one page
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            income_stability = IncomeStability.objects.get(user=request.user)
            serializer = IncomeStabilitySerializer(income_stability)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except IncomeStability.DoesNotExist:
            return Response(
                {"detail": "Income stability information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            income_stability = IncomeStability.objects.get(user=request.user)
            serializer = IncomeStabilitySerializer(income_stability, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            update_progress(request.user, "income_stability")
            # Trigger UHFS recalculation
            try:
                calculate_and_store_uhfs(request.user)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_200_OK)
        except IncomeStability.DoesNotExist:
            serializer = IncomeStabilitySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            update_progress(request.user, "income_stability")
            # Trigger UHFS recalculation
            try:
                calculate_and_store_uhfs(request.user)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial=False):
        try:
            income_stability = IncomeStability.objects.get(user=request.user)
            serializer = IncomeStabilitySerializer(income_stability, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Trigger UHFS recalculation
            try:
                calculate_and_store_uhfs(request.user)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_200_OK)
        except IncomeStability.DoesNotExist:
            return Response(
                {"detail": "Income stability information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND,
            )


class FinancialBehaviorView(APIView):
    """
    GET /api/finance/financial-behavior/ - Get financial behavior info (Q16-19)
    POST /api/finance/financial-behavior/ - Create or update financial behavior info
    All questions on one page
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            financial_behavior = FinancialBehavior.objects.get(user=request.user)
            serializer = FinancialBehaviorSerializer(financial_behavior)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FinancialBehavior.DoesNotExist:
            return Response(
                {"detail": "Financial behavior information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            financial_behavior = FinancialBehavior.objects.get(user=request.user)
            serializer = FinancialBehaviorSerializer(financial_behavior, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            update_progress(request.user, "financial_behavior")
            # Trigger UHFS recalculation
            try:
                calculate_and_store_uhfs(request.user)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FinancialBehavior.DoesNotExist:
            serializer = FinancialBehaviorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            update_progress(request.user, "financial_behavior")
            # Trigger UHFS recalculation
            try:
                calculate_and_store_uhfs(request.user)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial=False):
        try:
            financial_behavior = FinancialBehavior.objects.get(user=request.user)
            serializer = FinancialBehaviorSerializer(financial_behavior, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Trigger UHFS recalculation
            try:
                calculate_and_store_uhfs(request.user)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FinancialBehavior.DoesNotExist:
            return Response(
                {"detail": "Financial behavior information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ReliabilityTenureView(APIView):
    """
    GET /api/finance/reliability-tenure/ - Get reliability & tenure info (Q20-23)
    POST /api/finance/reliability-tenure/ - Create or update reliability & tenure info
    All questions on one page
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            reliability_tenure = ReliabilityTenure.objects.get(user=request.user)
            serializer = ReliabilityTenureSerializer(reliability_tenure)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReliabilityTenure.DoesNotExist:
            return Response(
                {"detail": "Reliability & tenure information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            reliability_tenure = ReliabilityTenure.objects.get(user=request.user)
            serializer = ReliabilityTenureSerializer(reliability_tenure, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            update_progress(request.user, "reliability_tenure")
            # Trigger UHFS recalculation
            try:
                calculate_and_store_uhfs(request.user)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReliabilityTenure.DoesNotExist:
            serializer = ReliabilityTenureSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            update_progress(request.user, "reliability_tenure")
            # Trigger UHFS recalculation
            try:
                calculate_and_store_uhfs(request.user)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial=False):
        try:
            reliability_tenure = ReliabilityTenure.objects.get(user=request.user)
            serializer = ReliabilityTenureSerializer(reliability_tenure, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Trigger UHFS recalculation
            try:
                calculate_and_store_uhfs(request.user)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReliabilityTenure.DoesNotExist:
            return Response(
                {"detail": "Reliability & tenure information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ProtectionReadinessView(APIView):
    """
    GET /api/finance/protection-readiness/ - Get protection readiness info (Q24-27)
    POST /api/finance/protection-readiness/ - Create or update protection readiness info
    All questions on one page
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            protection_readiness = ProtectionReadiness.objects.get(user=request.user)
            serializer = ProtectionReadinessSerializer(protection_readiness)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProtectionReadiness.DoesNotExist:
            return Response(
                {"detail": "Protection readiness information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            protection_readiness = ProtectionReadiness.objects.get(user=request.user)
            serializer = ProtectionReadinessSerializer(protection_readiness, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            update_progress(request.user, "protection_readiness")
            # Trigger UHFS recalculation
            try:
                calculate_and_store_uhfs(request.user)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProtectionReadiness.DoesNotExist:
            serializer = ProtectionReadinessSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            update_progress(request.user, "protection_readiness")
            # Trigger UHFS recalculation
            try:
                calculate_and_store_uhfs(request.user)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial=False):
        try:
            protection_readiness = ProtectionReadiness.objects.get(user=request.user)
            serializer = ProtectionReadinessSerializer(protection_readiness, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Trigger UHFS recalculation
            try:
                calculate_and_store_uhfs(request.user)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProtectionReadiness.DoesNotExist:
            return Response(
                {"detail": "Protection readiness information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND,
            )


# OLD VIEWS - REMOVED (Models no longer exist)
# These views referenced old models that have been replaced by the new consolidated structure:
# - BankingFinancialAccess -> Replaced by FinancialBehavior
# - CreditLiabilities -> Replaced by FinancialBehavior  
# - SavingsInsurance -> Replaced by ProtectionReadiness
# - ExpensesObligations -> Removed (not in new structure)
# - BehavioralPsychometric -> Replaced by FinancialBehavior
# - GovernmentSchemeEligibility -> Removed (not in new structure)

# Use new endpoints instead:
# - /api/finance/financial-behavior/ (Q16-19)
# - /api/finance/protection-readiness/ (Q24-27)


class UHFSScoreView(APIView):
    """
    GET /api/finance/uhfs-score/ - Get current UHFS score
    POST /api/finance/uhfs-score/ - Calculate and update UHFS score
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get user profile data from PersonalDemographic
        mobile_number = user.phone or user.username
        
        # Initialize user profile fields
        full_name = None
        age = None
        gender = None
        state = None
        city_district = None
        
        # Try to get data from PersonalDemographic
        try:
            personal_demo = PersonalDemographic.objects.get(user=user)
            full_name = personal_demo.full_name
            age = personal_demo.age
            gender = personal_demo.gender
            state = personal_demo.state
            city_district = personal_demo.city_district
        except PersonalDemographic.DoesNotExist:
            # Fallback to User model fields for name only
            if user.first_name or user.last_name:
                full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        
        try:
            uhfs = UHFSScore.objects.get(user=request.user)
            # Return same format as POST response with user profile
            result = {
                "user": {
                    "id": str(user.id),
                    "phone_number": mobile_number,
                    "full_name": full_name,
                    "age": age,
                    "gender": gender,
                    "state": state,
                    "city_district": city_district,
                },
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
            # Return user profile even if UHFS score doesn't exist
            return Response(
                {
                    "user": {
                        "id": str(user.id),
                        "phone_number": mobile_number,
                        "full_name": full_name,
                        "age": age,
                        "gender": gender,
                        "state": state,
                        "city_district": city_district,
                    },
                    "detail": "UHFS score not calculated yet. Use POST to calculate.",
                },
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


class DashboardView(APIView):
    """
    GET /api/finance/dashboard/
    Returns comprehensive user dashboard data including profile, UHFS score, and other relevant information.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get user profile data from PersonalDemographic
        mobile_number = user.phone or user.username
        
        # Initialize user profile fields
        full_name = None
        age = None
        gender = None
        state = None
        city_district = None
        
        # Try to get data from PersonalDemographic
        try:
            personal_demo = PersonalDemographic.objects.get(user=user)
            full_name = personal_demo.full_name
            age = personal_demo.age
            gender = personal_demo.gender
            state = personal_demo.state
            city_district = personal_demo.city_district
        except PersonalDemographic.DoesNotExist:
            # Fallback to User model fields for name only
            if user.first_name or user.last_name:
                full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        
        # Get UHFS score
        uhfs_data = None
        try:
            uhfs = UHFSScore.objects.get(user=user)
            uhfs_data = {
                "uhfs_score": uhfs.score,
                "components": uhfs.components or {},
                "composite": float(uhfs.composite) if uhfs.composite else 0.0,
                "overall_risk": uhfs.overall_risk or "Unknown",
                "domain_risk": uhfs.domain_risk or {},
                "last_updated": uhfs.last_updated.isoformat() if uhfs.last_updated else None,
            }
        except UHFSScore.DoesNotExist:
            uhfs_data = None
        
        # Get onboarding progress
        from finance.utils import get_onboarding_progress_details
        onboarding_details = get_onboarding_progress_details(user)
        
        # Get suggested products if UHFS score exists
        suggested_products = []
        if uhfs_data and uhfs_data.get("uhfs_score"):
            try:
                from finance.services.products_util import get_suggested_products_util
                from finance.serializers import ProductSerializer
                products_qs = get_suggested_products_util(uhfs_data["uhfs_score"])
                suggested_products = ProductSerializer(products_qs, many=True).data
            except Exception:
                pass
        
        return Response(
            {
                "user": {
                    "id": str(user.id),
                    "phone_number": mobile_number,
                    "full_name": full_name,
                    "age": age,
                    "gender": gender,
                    "state": state,
                    "city_district": city_district,
                },
                "uhfs": uhfs_data,
                "onboarding": onboarding_details,
                "suggested_products": suggested_products,
            },
            status=status.HTTP_200_OK,
        )


class RiskRecommendationView(APIView):
    """
    POST /api/finance/risk-recommendation/
    
    Get product recommendations based on risk category and risk level.
    
    Request Body:
    {
        "risk": "Income Stability" | "Financial Behavior" | "Reliability & Tenure" | "Protection Readiness",
        "risk_level": "High" | "Medium" | "Low" (or with emoji: "🔴 High", "🟠 Medium", "🟢 Low")
    }
    
    Response:
    {
        "risk_category": "Income Stability",
        "risk_trigger": "Income volatility > 40% or <15 days active/month",
        "risk_level": "🔴 High",
        "recommended_instruments": ["PMMY (Mudra Loan)", "PM SVANidhi", "Post Office RD", ...],
        "behavioral_tag": "Manage Income Volatility / Emergency Corpus",
        "intro_section": "Your income is fluctuating right now..."
    }
    """
    permission_classes = []  # AllowAny - can be accessed without authentication
    
    def post(self, request):
        serializer = RiskRecommendationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        risk_category = serializer.validated_data["risk"]
        risk_level = serializer.validated_data["risk_level"]
        
        # Normalize risk_level (handle both with and without emoji)
        risk_level_normalized = risk_level
        if risk_level in ["High", "🔴 High"]:
            risk_level_normalized = "🔴 High"
        elif risk_level in ["Medium", "🟠 Medium"]:
            risk_level_normalized = "🟠 Medium"
        elif risk_level in ["Low", "🟢 Low"]:
            risk_level_normalized = "🟢 Low"
        
        # Query for matching recommendations
        recommendations = RiskRecommendation.objects.filter(
            risk_category=risk_category,
            risk_level=risk_level_normalized,
            is_active=True
        ).order_by("order")
        
        if not recommendations.exists():
            # Try without emoji if not found
            risk_level_fallback = risk_level.replace("🔴 ", "").replace("🟠 ", "").replace("🟢 ", "")
            recommendations = RiskRecommendation.objects.filter(
                risk_category=risk_category,
                risk_level__in=[risk_level_normalized, risk_level_fallback],
                is_active=True
            ).order_by("order")
        
        if not recommendations.exists():
            return Response(
                {
                    "error": "No recommendations found",
                    "message": f"No recommendations found for risk category '{risk_category}' and risk level '{risk_level}'"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return the first matching recommendation (or all if multiple)
        response_serializer = RiskRecommendationResponseSerializer(recommendations, many=True)
        
        # If only one result, return as object; if multiple, return as array
        if len(response_serializer.data) == 1:
            return Response(response_serializer.data[0], status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    "count": len(response_serializer.data),
                    "results": response_serializer.data
                },
                status=status.HTTP_200_OK
            )


