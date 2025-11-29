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

    # -------------------------
    # INCOME STABILITY (I)
    # weights: A=20%, B=50%, C=25%, D=5%
    # -------------------------
    monthly_income_map = {
        "5000-10000": 0.1,
        "10001-20000": 0.4,
        "20001-30000": 0.6,
        "30001-50000": 0.9,
        "50000+": 1.0,
        # alternative labels (in case front-end uses different text)
        "<10000": 0.1,
        "10k-20k": 0.4,
        "20k-30k": 0.6,
        "30k-50k": 0.9,
        ">50000": 1.0,
    }
    drop_freq_map = {
        "never": 1.0,
        "once": 0.7,
        "often": 0.4,
        "every_month": 0.2,
        "almost_every_month": 0.2,  # Sheet says "Almost every month" = 0.2
    }
    working_days_map = {
        "1-2": 0.25,
        "3-4": 0.5,
        "5-6": 0.75,
        "7": 1.0,
        "everyday": 1.0,
    }
    trend_map = {
        "increased": 1.0,
        "stable": 0.8,
        "decreased": 0.4,
    }

    A = monthly_income_map.get((_safe_get(income, "monthly_income_range") or "").strip(), 0.0)
    
    # Map income_variability to drop frequency (B)
    # If income_drop_frequency field doesn't exist, derive from income_variability
    income_drop_freq = _safe_get(income, "income_drop_frequency", None)
    if income_drop_freq is None:
        # Derive from income_variability
        variability = (_safe_get(income, "income_variability") or "").strip().lower()
        if variability in ["fixed", "same"]:
            income_drop_freq = "never"
        elif variability in ["variable", "fluctuates"]:
            income_drop_freq = "often"
        elif variability in ["irregular"]:
            income_drop_freq = "almost_every_month"
        else:
            income_drop_freq = ""
    B = drop_freq_map.get(str(income_drop_freq).strip().lower(), 0.0)
    
    # Map working_days_per_month to working_days_per_week (C)
    # Convert monthly days to weekly (divide by ~4)
    working_days_month = _safe_get(income, "working_days_per_month", None)
    if working_days_month is not None:
        working_days_week_approx = working_days_month / 4.0
        if working_days_week_approx <= 2:
            working_days_week_str = "1-2"
        elif working_days_week_approx <= 4:
            working_days_week_str = "3-4"
        elif working_days_week_approx <= 6:
            working_days_week_str = "5-6"
        else:
            working_days_week_str = "7"
    else:
        working_days_week_str = _safe_get(income, "working_days_per_week", "")
    C = working_days_map.get(str(working_days_week_str).strip().lower(), 0.0)
    
    # Income trend (D) - use income_variability as proxy if income_trend doesn't exist
    income_trend = _safe_get(income, "income_trend", None)
    if income_trend is None:
        variability = (_safe_get(income, "income_variability") or "").strip().lower()
        if variability in ["fixed", "same"]:
            income_trend = "stable"
        elif "increase" in variability or "grow" in variability:
            income_trend = "increased"
        elif "decrease" in variability or "decline" in variability:
            income_trend = "decreased"
        else:
            income_trend = "stable"
    D = trend_map.get(str(income_trend).strip().lower(), 0.8)

    # Compute I as specified: 0.20*A + 0.50*B + 0.25*C + 0.05*D
    I = (0.20 * A) + (0.50 * B) + (0.25 * C) + (0.05 * D)

    # -------------------------
    # FINANCIAL BEHAVIOR (F)
    # weights: A=40%, B=10%, C=30%, D=20%
    # -------------------------
    savings_amount_map = {
        "<500": 0.2,
        "500-1000": 0.5,
        "1000-3000": 0.8,
        ">3000": 1.0,
        "less_than_500": 0.2,
        "500-1000": 0.5,
    }
    savings_method_map = {
        "bank": 1.0,
        "wallet": 0.8,
        "cash": 0.4,
        "none": 0.0,
    }
    # missed EMI: if missed -> 0.0, no missed -> 1.0
    missed_map = {
        True: 0.0,
        False: 1.0,
        "yes": 0.0,
        "no": 1.0
    }
    bill_map = {
        "always": 1.0,
        "mostly": 0.75,
        "sometimes": 0.5,
        "rarely": 0.2,
    }

    FA = savings_amount_map.get((_safe_get(savings, "savings_amount_per_month") or "").strip().lower(), 0.0)
    
    # Derive savings_method from banking access if savings_method doesn't exist
    savings_method = _safe_get(savings, "savings_method", None)
    if savings_method is None:
        has_bank = _safe_get(banking, "has_bank_account", False)
        has_upi = _safe_get(banking, "has_upi_wallet", False)
        if has_bank:
            savings_method = "bank"
        elif has_upi:
            savings_method = "wallet"
        else:
            savings_method = "cash"
    FB = savings_method_map.get(str(savings_method).strip().lower(), 0.0)
    
    # missed EMI field may be boolean or string; try both
    raw_missed = _safe_get(credit, "missed_payments_6m", None)
    if isinstance(raw_missed, bool):
        FC = missed_map.get(raw_missed, 0.0)
    else:
        FC = missed_map.get((str(raw_missed) or "").strip().lower(), 0.0)
    
    # Use payment_miss_frequency from behavior as proxy for utility_payment_behavior
    utility_payment_behavior = _safe_get(expenses, "utility_payment_behavior", None)
    if utility_payment_behavior is None:
        # Map payment_miss_frequency inversely (never miss = always pay)
        payment_freq = (_safe_get(behavior, "payment_miss_frequency") or "").strip().lower()
        if payment_freq == "never":
            utility_payment_behavior = "always"
        elif payment_freq == "rarely":
            utility_payment_behavior = "mostly"
        elif payment_freq == "sometimes":
            utility_payment_behavior = "sometimes"
        else:
            utility_payment_behavior = "rarely"
    FD = bill_map.get(str(utility_payment_behavior).strip().lower(), 0.75)

    F = (0.40 * FA) + (0.10 * FB) + (0.30 * FC) + (0.20 * FD)

    # -------------------------
    # RELIABILITY & TENURE (R)
    # weights: A=40%, B=30%, C=20%, D=10%
    # -------------------------
    tenure_map = {
        "<3": 0.25,
        "3-6": 0.5,
        "6-12": 0.75,
        ">12": 1.0,
        "less_than_3_months": 0.25,
        "3-6_months": 0.5,
        "6-12_months": 0.75,
        "more_than_1_year": 1.0,
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
        1: 0.25,
        2: 0.5,
        3: 0.75,
        4: 0.9,
        5: 1.0,
    }

    # Platform tenure - use default if not available
    platform_tenure = _safe_get(income, "platform_tenure_bucket", None)
    if platform_tenure is None:
        platform_tenure = "3-6"  # Default to medium
    RA = tenure_map.get(str(platform_tenure).strip().lower(), 0.5)
    
    # Active days - derive from working_days_per_month if active_days doesn't exist
    active_days = _safe_get(income, "active_days", None)
    if active_days is None:
        working_days_month = _safe_get(income, "working_days_per_month", None)
        if working_days_month is not None:
            working_days_week_approx = working_days_month / 4.0
            if working_days_week_approx <= 2:
                active_days = "1-2"
            elif working_days_week_approx <= 4:
                active_days = "3-4"
            elif working_days_week_approx <= 6:
                active_days = "5-6"
            else:
                active_days = "7"
        else:
            active_days = "3-4"  # Default
    RB = active_days_map.get(str(active_days).strip().lower(), 0.5)
    
    # Cancellation rate - use default if not available
    cancellation_rate = _safe_get(income, "cancellation_rate", None)
    if cancellation_rate is None:
        cancellation_rate = "rarely"  # Default
    RC = cancel_map.get(str(cancellation_rate).strip().lower(), 1.0)
    
    # Customer rating - use digital_comfort_level as proxy if customer_rating doesn't exist
    raw_rating = _safe_get(income, "customer_rating", None)
    if raw_rating is None:
        raw_rating = _safe_get(behavior, "digital_comfort_level", None)
    try:
        RD = rating_map.get(int(raw_rating), 0.5) if raw_rating is not None else 0.5
    except (ValueError, TypeError):
        RD = rating_map.get(str(raw_rating).strip(), 0.5) if raw_rating else 0.5

    R = (0.40 * RA) + (0.30 * RB) + (0.20 * RC) + (0.10 * RD)

    # -------------------------
    # PROTECTION READINESS (P)
    # Weights: A=30%, B=30%, C=30%, D=10%
    # -------------------------
    insurance_map = {
        True: 1.0,
        False: 0.0,
        "yes": 1.0,
        "no": 0.0,
        "not_sure": 0.3,
    }
    emergency_map = {
        "immediately": 1.0,
        "1week": 0.8,
        "1 month": 0.4,
        "1month": 0.4,
        "cannot": 0.0,
        "cannot_manage": 0.0,
    }
    emergency_fund_map = {
        "0-500": 0.2,
        "500-1000": 0.4,
        "501-1000": 0.4,  # Alternative format
        "1000-5000": 0.7,
        "1001-5000": 0.7,  # Alternative format
        "5000+": 1.0,
    }

    # Check has_health_insurance - parse from has_insurance field
    has_health_insurance = _safe_get(savings, "has_health_insurance", None)
    if has_health_insurance is None:
        insurance_str = _safe_get(savings, "has_insurance", "")
        if insurance_str:
            has_health_insurance = "health" in str(insurance_str).lower()
        else:
            has_health_insurance = False
    if isinstance(has_health_insurance, str):
        PA = insurance_map.get(has_health_insurance.strip().lower(), 0.0)
    else:
        PA = insurance_map.get(has_health_insurance, 0.0)
    
    # Check has_life_cover - parse from has_insurance field
    has_life_cover = _safe_get(savings, "has_life_cover", None)
    if has_life_cover is None:
        insurance_str = _safe_get(savings, "has_insurance", "")
        if insurance_str:
            has_life_cover = "life" in str(insurance_str).lower()
        else:
            has_life_cover = False
    if isinstance(has_life_cover, str):
        PB = insurance_map.get(has_life_cover.strip().lower(), 0.0)
    else:
        PB = insurance_map.get(has_life_cover, 0.0)
    
    # Emergency capability - use default if not available
    emergency_capability = _safe_get(savings, "emergency_capability", None)
    if emergency_capability is None:
        # Derive from regular_savings_habit
        if _safe_get(savings, "regular_savings_habit", False):
            emergency_capability = "1week"
        else:
            emergency_capability = "1month"
    PC = emergency_map.get(str(emergency_capability).strip().lower(), 0.4)
    
    # Emergency saving amount - use savings_amount_per_month as proxy
    emergency_saving_amount = _safe_get(savings, "emergency_saving_amount", None)
    if emergency_saving_amount is None:
        savings_amt = (_safe_get(savings, "savings_amount_per_month") or "").strip().lower()
        if "<500" in savings_amt or "less_than_500" in savings_amt:
            emergency_saving_amount = "0-500"
        elif "500-1000" in savings_amt or "500" in savings_amt:
            emergency_saving_amount = "500-1000"
        elif "1000" in savings_amt or "3000" in savings_amt:
            emergency_saving_amount = "1000-5000"
        else:
            emergency_saving_amount = "5000+"
    PD = emergency_fund_map.get(str(emergency_saving_amount).strip().lower(), 0.2)

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

    # Persist UHFSScore (create or update)
    score_obj, created = UHFSScore.objects.update_or_create(
        user=user,
        defaults={
            "score": int(uhfs_value),
            "last_updated": timezone.now(),
        },
    )

    # Build result dict
    result = {
        "user_id": str(user.id),
        "components": {
            "I": round(I, 5),
            "F": round(F, 5),
            "R": round(R, 5),
            "P": round(P, 5),
            "L": round(L, 5),
        },
        "weights": {"I": 0.25, "F": 0.25, "R": 0.15, "P": 0.20, "L": 0.15},
        "composite": round(composite, 5),
        "uhfs_score": int(uhfs_value),
        "domain_risk": domain_classes,
        "overall_risk": overall,
        "saved": True,
    }

    return result
