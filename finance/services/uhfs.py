from typing import Dict, Any

from django.db import transaction
from django.utils import timezone

from finance.models import (
    PersonalDemographic,
    IncomeEmployment,
    BankingFinancialAccess,
    CreditLiabilities,
    SavingsInsurance,
    ExpensesObligations,
    BehavioralPsychometric,
    GovernmentSchemeEligibility,
    UserFinancialLiteracy,
    UHFSScore,
)


# Helper: safe getter
def _safe_get(obj, attr, default=None):
    return getattr(obj, attr, default) if obj is not None else default


# Risk classification helpers (per your sheet)
def _classify_income(i: float) -> str:
    if i < 0.45:
        return "High"
    if i < 0.70:
        return "Medium"
    return "Low"


def _classify_financial(f: float) -> str:
    if f < 0.50:
        return "High"
    if f < 0.75:
        return "Medium"
    return "Low"


def _classify_reliability(r: float) -> str:
    if r < 0.55:
        return "Medium"
    return "Low"


def _classify_protection(p: float) -> str:
    if p < 0.50:
        return "High"
    if p < 0.75:
        return "Medium"
    return "Low"


def _classify_literacy(l: float) -> str:
    if l < 0.50:
        return "High"
    if l < 0.75:
        return "Medium"
    return "Low"


def _overall_risk(domain_classes: Dict[str, str]) -> str:
    # Count High and Medium across domains I,F,R,P,L
    counts = {"High": 0, "Medium": 0, "Low": 0}
    for v in domain_classes.values():
        counts[v] = counts.get(v, 0) + 1
    if counts["High"] >= 2:
        return "High"
    if (counts["High"] + counts["Medium"]) >= 2:
        return "Medium"
    return "Low"


@transaction.atomic
def calculate_and_store_uhfs(user) -> Dict[str, Any]:
    """
    Calculate UHFS for the given user and persist it.

    Returns a dict with detailed breakdown, composite, final score, and risk labels.
    """
    # --- fetch or create domain objects (create empty records if missing) ---
    personal = PersonalDemographic.objects.filter(user=user).first()
    income = IncomeEmployment.objects.filter(user=user).first()
    banking = BankingFinancialAccess.objects.filter(user=user).first()
    credit = CreditLiabilities.objects.filter(user=user).first()
    savings = SavingsInsurance.objects.filter(user=user).first()
    expenses = ExpensesObligations.objects.filter(user=user).first()
    behavior = BehavioralPsychometric.objects.filter(user=user).first()
    govt = GovernmentSchemeEligibility.objects.filter(user=user).first()
    literacy = UserFinancialLiteracy.objects.filter(user=user).first()

    # create missing domain rows (so future writes are simpler)
    if not income:
        income = IncomeEmployment.objects.create(user=user)
    if not savings:
        savings = SavingsInsurance.objects.create(user=user)
    if not credit:
        credit = CreditLiabilities.objects.create(user=user)
    if not expenses:
        expenses = ExpensesObligations.objects.create(user=user)
    if not behavior:
        behavior = BehavioralPsychometric.objects.create(user=user)
    if not personal:
        personal = PersonalDemographic.objects.create(user=user)
    if not literacy:
        literacy = UserFinancialLiteracy.objects.create(user=user)
    if not banking:
        banking = BankingFinancialAccess.objects.create(user=user)
    if not govt:
        govt = GovernmentSchemeEligibility.objects.create(user=user)

    # INCOME STABILITY (I) - weights: A=20%, B=50%, C=25%, D=5%
    monthly_income_map = {
        "5000-10000": 0.1,
        "10001-20000": 0.4,
        "20001-30000": 0.6,
        "30001-50000": 0.9,
        "50000+": 1.0,
    }
    drop_freq_map = {
        "never": 1.0,
        "once": 0.7,
        "often": 0.4,
        "almost every month": 0.2,
        "every month": 0.2,
    }
    working_days_map = {
        "1-2": 0.25,
        "3-4": 0.5,
        "5-6": 0.75,
        "every day": 1.0,
        "7": 1.0,
    }
    trend_map = {
        "increased": 1.0,
        "stable": 0.8,
        "decreased": 0.4,
    }
    A = monthly_income_map.get((_safe_get(income, "monthly_income_range") or "").strip(), 0.0)
    B = drop_freq_map.get((_safe_get(income, "income_drop_frequency") or "").strip().lower(), 0.0)
    C = working_days_map.get((_safe_get(income, "working_days_per_week") or "").strip().lower(), 0.0)
    D = trend_map.get((_safe_get(income, "income_trend") or "").strip().lower(), 0.8)
    I = (0.20 * A) + (0.50 * B) + (0.25 * C) + (0.05 * D)

    # FINANCIAL BEHAVIOR (F) - weights: A=40%, B=10%, C=30%, D=20%
    savings_amount_map = {
        "less than 500": 0.2,
        "500-1000": 0.5,
        "1000-3000": 0.8,
        "more than 3000": 1.0,
    }
    savings_method_map = {
        "bank": 1.0,
        "wallet": 0.8,
        "cash": 0.4,
        "not saving currently": 0.0,
    }
    missed_map = {
        "no": 1.0,
        "yes": 0.0,
        "not applicable": 1.0,
    }
    bill_map = {
        "always": 1.0,
        "mostly": 0.75,
        "sometimes": 0.5,
        "rarely": 0.2,
    }
    FA = savings_amount_map.get((_safe_get(savings, "savings_amount_per_month") or "").strip().lower(), 0.0)
    FB = savings_method_map.get((_safe_get(savings, "savings_method") or "").strip().lower(), 0.0)
    FC = missed_map.get((_safe_get(credit, "missed_payments_3m") or "").strip().lower(), 1.0)
    FD = bill_map.get((_safe_get(expenses, "bill_payment_timeliness") or "").strip().lower(), 0.5)
    F = (0.40 * FA) + (0.10 * FB) + (0.30 * FC) + (0.20 * FD)

    # RELIABILITY & TENURE (R) - weights: A=40%, B=30%, C=20%, D=10%
    tenure_map = {
        "less than 3 months": 0.25,
        "3-6 months": 0.5,
        "6-12 months": 0.75,
        "more than 1 year": 1.0,
    }
    active_days_map = {
        "1-2": 0.25,
        "3-4": 0.5,
        "5-6": 0.75,
        "7": 1.0,
    }
    cancel_map = {
        "rarely": 1.0,
        "sometimes": 0.5,
        "often": 0.2,
    }
    rating_map = {
        "1": 0.25,
        "2": 0.5,
        "3": 0.75,
        "4": 0.9,
        "5": 1.0,
    }
    RA = tenure_map.get((_safe_get(income, "platform_tenure") or "").strip().lower(), 0.5)
    RB = active_days_map.get((_safe_get(income, "active_days_per_week") or "").strip().lower(), 0.5)
    RC = cancel_map.get((_safe_get(income, "cancellation_frequency") or "").strip().lower(), 1.0)
    RD = rating_map.get(str(_safe_get(income, "customer_rating", "3")).strip(), 0.5)
    R = (0.40 * RA) + (0.30 * RB) + (0.20 * RC) + (0.10 * RD)

    # PROTECTION READINESS (P) - weights: A=30%, B=30%, C=30%, D=10%
    insurance_map = {
        "yes": 1.0,
        "no": 0.0,
        "not sure": 0.3,
    }
    emergency_map = {
        "immediately": 1.0,
        "within 1 week": 0.8,
        "within 1 month": 0.4,
        "cannot manage": 0.0,
    }
    emergency_fund_map = {
        "0-500": 0.2,
        "501-1000": 0.4,
        "1001-5000": 0.7,
        "5000+": 1.0,
    }
    PA = insurance_map.get((_safe_get(savings, "has_health_insurance") or "").strip().lower(), 0.0)
    PB = insurance_map.get((_safe_get(savings, "has_life_cover") or "").strip().lower(), 0.0)
    PC = emergency_map.get((_safe_get(savings, "emergency_expense_capability") or "").strip().lower(), 0.0)
    PD = emergency_fund_map.get((_safe_get(savings, "emergency_fund_amount") or "").strip().lower(), 0.2)
    P = (0.30 * PA) + (0.30 * PB) + (0.30 * PC) + (0.10 * PD)

    # -------------------------
    # FINANCIAL LITERACY (L)
    # L is normalized average_quiz_score / 100 (0..1)
    # -------------------------
    L_raw = _safe_get(literacy, "average_quiz_score", 0.0) or 0.0
    try:
        L = float(L_raw) / 100.0
    except Exception:
        L = 0.0
    if L < 0:
        L = 0.0
    if L > 1:
        L = 1.0

    # -------------------------
    # Composite and final UHFS
    # Composite = 0.25I + 0.25F + 0.15R + 0.20P + 0.15L
    # UHFS = ROUND(300 + composite * 600)
    # -------------------------
    composite = (0.25 * I) + (0.25 * F) + (0.15 * R) + (0.20 * P) + (0.15 * L)

    # Ensure numeric stability
    composite = max(0.0, min(composite, 1.0))

    uhfs_value = round(300 + composite * 600)

    # Determine per-domain risk labels
    domain_classes = {
        "income": _classify_income(I),
        "financial_behavior": _classify_financial(F),
        "reliability": _classify_reliability(R),
        "protection": _classify_protection(P),
        "literacy": _classify_literacy(L),
    }

    overall = _overall_risk(domain_classes)

    # Prepare components dict
    components_dict = {
        "I": round(I, 5),
        "F": round(F, 5),
        "R": round(R, 5),
        "P": round(P, 5),
        "L": round(L, 5),
    }

    # Persist UHFSScore (create or update) with all details
    score_obj, created = UHFSScore.objects.update_or_create(
        user=user,
        defaults={
            "score": int(uhfs_value),
            "components": components_dict,
            "composite": round(composite, 5),
            "domain_risk": domain_classes,
            "overall_risk": overall,
            "last_updated": timezone.now(),
        },
    )

    # Build result dict
    result = {
        "user_id": str(user.id),
        "components": components_dict,
        "weights": {"I": 0.25, "F": 0.25, "R": 0.15, "P": 0.20, "L": 0.15},
        "composite": round(composite, 5),
        "uhfs_score": int(uhfs_value),
        "domain_risk": domain_classes,
        "overall_risk": overall,
        "saved": True,
    }

    return result
