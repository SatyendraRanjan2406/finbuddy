"""
UHFS Scoring Logic V2 - Based on new consolidated questionnaire structure.
Uses new models: IncomeStability, FinancialBehavior, ReliabilityTenure, ProtectionReadiness
"""
from typing import Dict, Any, Optional
from django.db import transaction
from django.utils import timezone

from finance.models import (
    PersonalDemographic,
    IncomeEmployment,
    IncomeStability,
    FinancialBehavior,
    ReliabilityTenure,
    ProtectionReadiness,
    UserFinancialLiteracy,
    UHFSScore,
)


def calculate_income_stability_score(income_stability: Optional[IncomeStability]) -> Dict[str, Any]:
    """
    Calculate Income Stability (I) subcategory score.
    Formula: 0.20*A + 0.50*B + 0.25*C + 0.05*D
    
    Q12 (A): Monthly income - weight 20%
    Q13 (B): Income drop frequency - weight 50%
    Q14 (C): Working days per week - weight 25%
    Q15 (D): Income trend - weight 5%
    """
    if not income_stability:
        return {"score": 0.0, "subcategory_score": 0.0, "scores": {}}
    
    # Q12 (A): Monthly income scoring
    monthly_income_map = {
        "₹5,000–10,000": 0.1,
        "₹10,001–20,000": 0.4,
        "₹20,001–30,000": 0.6,
        "₹30,001–50,000": 0.9,
        "₹50,000+": 1.0,
    }
    score_a = monthly_income_map.get(income_stability.monthly_income, 0.0)
    
    # Q13 (B): Income drop frequency scoring
    drop_freq_map = {
        "Never": 1.0,
        "Once": 0.7,
        "Often": 0.4,
        "Almost every month": 0.2,
    }
    score_b = drop_freq_map.get(income_stability.income_drop_frequency, 0.0)
    
    # Q14 (C): Working days per week scoring
    working_days_map = {
        "1–2 days": 0.25,
        "3–4 days": 0.5,
        "5–6 days": 0.75,
        "Every day": 1.0,
    }
    score_c = working_days_map.get(income_stability.working_days_per_week, 0.0)
    
    # Q15 (D): Income trend scoring
    trend_map = {
        "Increased": 1.0,
        "Stable": 0.8,
        "Decreased": 0.4,
    }
    score_d = trend_map.get(income_stability.income_trend, 0.0)
    
    # Calculate weighted subcategory score
    subcategory_score = (0.20 * score_a) + (0.50 * score_b) + (0.25 * score_c) + (0.05 * score_d)
    
    # Save scores to model
    income_stability.score_a = score_a
    income_stability.score_b = score_b
    income_stability.score_c = score_c
    income_stability.score_d = score_d
    income_stability.subcategory_score = subcategory_score
    income_stability.save(update_fields=['score_a', 'score_b', 'score_c', 'score_d', 'subcategory_score'])
    
    return {
        "score": subcategory_score,
        "subcategory_score": subcategory_score,
        "scores": {"A": score_a, "B": score_b, "C": score_c, "D": score_d},
    }


def calculate_financial_behavior_score(financial_behavior: Optional[FinancialBehavior]) -> Dict[str, Any]:
    """
    Calculate Financial Behavior (F) subcategory score.
    Formula: 0.40*A + 0.10*B + 0.30*C + 0.20*D
    
    Q16 (A): Monthly savings - weight 40%
    Q17 (B): Saving methods - weight 10%
    Q18 (C): Missed payments - weight 30%
    Q19 (D): Bill payment timeliness - weight 20%
    """
    if not financial_behavior:
        return {"score": 0.0, "subcategory_score": 0.0, "scores": {}}
    
    # Q16 (A): Monthly savings scoring
    savings_map = {
        "Less than ₹500": 0.2,
        "₹500–₹1,000": 0.5,
        "₹1,000–₹3,000": 0.8,
        "More than ₹3,000": 1.0,
    }
    score_a = savings_map.get(financial_behavior.monthly_savings, 0.0)
    
    # Q17 (B): Saving methods scoring (checkboxes - take highest score)
    saving_methods = financial_behavior.saving_methods or []
    method_scores = {
        "Bank account": 1.0,
        "Wallet (Paytm, GPay, etc.)": 0.8,
        "Cash at home": 0.4,
        "Not saving currently": 0.0,
    }
    score_b = max([method_scores.get(method, 0.0) for method in saving_methods], default=0.0)
    
    # Q18 (C): Missed payments scoring
    missed_payment_map = {
        "No": 1.0,
        "Yes": 0.0,
        "Not applicable": 1.0,  # Treat as no missed payments
    }
    score_c = missed_payment_map.get(financial_behavior.missed_payments, 0.0)
    
    # Q19 (D): Bill payment timeliness scoring
    bill_map = {
        "Always": 1.0,
        "Mostly": 0.75,
        "Sometimes": 0.5,
        "Rarely": 0.2,
    }
    score_d = bill_map.get(financial_behavior.bill_payment_timeliness, 0.0)
    
    # Calculate weighted subcategory score
    subcategory_score = (0.40 * score_a) + (0.10 * score_b) + (0.30 * score_c) + (0.20 * score_d)
    
    # Save scores to model
    financial_behavior.score_a = score_a
    financial_behavior.score_b = score_b
    financial_behavior.score_c = score_c
    financial_behavior.score_d = score_d
    financial_behavior.subcategory_score = subcategory_score
    financial_behavior.save(update_fields=['score_a', 'score_b', 'score_c', 'score_d', 'subcategory_score'])
    
    return {
        "score": subcategory_score,
        "subcategory_score": subcategory_score,
        "scores": {"A": score_a, "B": score_b, "C": score_c, "D": score_d},
    }


def calculate_reliability_tenure_score(reliability_tenure: Optional[ReliabilityTenure]) -> Dict[str, Any]:
    """
    Calculate Reliability & Tenure (R) subcategory score.
    Formula: 0.40*A + 0.30*B + 0.20*C + 0.10*D
    
    Q20 (A): Platform tenure - weight 40%
    Q21 (B): Active days per week - weight 30%
    Q22 (C): Cancellation frequency - weight 20%
    Q23 (D): Customer rating - weight 10%
    """
    if not reliability_tenure:
        return {"score": 0.0, "subcategory_score": 0.0, "scores": {}}
    
    # Q20 (A): Platform tenure scoring
    tenure_map = {
        "Less than 3 months": 0.25,
        "3–6 months": 0.5,
        "6–12 months": 0.75,
        "More than 1 year": 1.0,
    }
    score_a = tenure_map.get(reliability_tenure.platform_tenure, 0.0)
    
    # Q21 (B): Active days per week scoring
    active_days_map = {
        "1–2": 0.25,
        "3–4": 0.5,
        "5–6": 0.75,
        "7 days": 1.0,
    }
    score_b = active_days_map.get(reliability_tenure.active_days_per_week, 0.0)
    
    # Q22 (C): Cancellation frequency scoring
    cancel_map = {
        "Rarely": 1.0,
        "Sometimes": 0.5,
        "Often": 0.2,
    }
    score_c = cancel_map.get(reliability_tenure.cancellation_frequency, 0.0)
    
    # Q23 (D): Customer rating scoring
    rating_map = {
        "1": 0.25,
        "2": 0.5,
        "3": 0.75,
        "4": 0.9,
        "5": 1.0,
    }
    score_d = rating_map.get(reliability_tenure.customer_rating, 0.0)
    
    # Calculate weighted subcategory score
    subcategory_score = (0.40 * score_a) + (0.30 * score_b) + (0.20 * score_c) + (0.10 * score_d)
    
    # Save scores to model
    reliability_tenure.score_a = score_a
    reliability_tenure.score_b = score_b
    reliability_tenure.score_c = score_c
    reliability_tenure.score_d = score_d
    reliability_tenure.subcategory_score = subcategory_score
    reliability_tenure.save(update_fields=['score_a', 'score_b', 'score_c', 'score_d', 'subcategory_score'])
    
    return {
        "score": subcategory_score,
        "subcategory_score": subcategory_score,
        "scores": {"A": score_a, "B": score_b, "C": score_c, "D": score_d},
    }


def calculate_protection_readiness_score(protection_readiness: Optional[ProtectionReadiness]) -> Dict[str, Any]:
    """
    Calculate Protection Readiness (P) subcategory score.
    Formula: 0.30*A + 0.30*B + 0.30*C + 0.10*D
    
    Q24 (A): Health insurance - weight 30%
    Q25 (B): Accident/life insurance - weight 30%
    Q26 (C): Emergency expense handling - weight 30%
    Q27 (D): Current savings/emergency funds - weight 10%
    """
    if not protection_readiness:
        return {"score": 0.0, "subcategory_score": 0.0, "scores": {}}
    
    # Q24 (A): Health insurance scoring
    insurance_map = {
        "Yes": 1.0,
        "No": 0.0,
        "Not sure": 0.3,
    }
    score_a = insurance_map.get(protection_readiness.has_health_insurance, 0.0)
    
    # Q25 (B): Accident/life insurance scoring
    score_b = insurance_map.get(protection_readiness.has_accident_life_insurance, 0.0)
    
    # Q26 (C): Emergency expense handling scoring
    emergency_map = {
        "Immediately": 1.0,
        "Within 1 week": 0.8,
        "Within 1 month": 0.4,
        "Cannot manage": 0.0,
    }
    score_c = emergency_map.get(protection_readiness.emergency_expense_handling, 0.0)
    
    # Q27 (D): Current savings/emergency funds scoring
    savings_fund_map = {
        "₹0–500": 0.2,
        "₹501–1,000": 0.4,
        "₹1,001–5,000": 0.7,
        "₹5,000+": 1.0,
    }
    score_d = savings_fund_map.get(protection_readiness.current_savings_fund, 0.0)
    
    # Calculate weighted subcategory score
    subcategory_score = (0.30 * score_a) + (0.30 * score_b) + (0.30 * score_c) + (0.10 * score_d)
    
    # Save scores to model
    protection_readiness.score_a = score_a
    protection_readiness.score_b = score_b
    protection_readiness.score_c = score_c
    protection_readiness.score_d = score_d
    protection_readiness.subcategory_score = subcategory_score
    protection_readiness.save(update_fields=['score_a', 'score_b', 'score_c', 'score_d', 'subcategory_score'])
    
    return {
        "score": subcategory_score,
        "subcategory_score": subcategory_score,
        "scores": {"A": score_a, "B": score_b, "C": score_c, "D": score_d},
    }


def calculate_financial_literacy_score(literacy: Optional[UserFinancialLiteracy]) -> float:
    """
    Calculate Financial Literacy (L) score.
    Based on modules completed and average quiz score.
    If 3 modules completed with quiz score < 70%, weight varies between 0-1.
    """
    if not literacy:
        return 0.0
    
    # Normalize average_quiz_score (0-100) to 0-1
    quiz_score_normalized = (literacy.average_quiz_score or 0.0) / 100.0
    
    # Apply penalty if modules completed but score is low
    modules_completed = literacy.modules_completed or 0
    if modules_completed > 0 and quiz_score_normalized < 0.70:
        # Penalty: reduce score based on how far below 70%
        penalty_factor = quiz_score_normalized / 0.70
        literacy_score = quiz_score_normalized * penalty_factor
    else:
        literacy_score = quiz_score_normalized
    
    # Ensure between 0 and 1
    literacy_score = max(0.0, min(1.0, literacy_score))
    
    # Save to model
    literacy.literacy_score = literacy_score
    literacy.save(update_fields=['literacy_score'])
    
    return literacy_score


def classify_risk(score: float, category: str) -> str:
    """
    Classify risk level based on subcategory score.
    """
    if category == "Income Stability":
        if score < 0.45:
            return "High"
        elif score < 0.70:
            return "Medium"
        else:
            return "Low"
    elif category == "Financial Behavior":
        if score < 0.50:
            return "High"
        elif score < 0.75:
            return "Medium"
        else:
            return "Low"
    elif category == "Reliability & Tenure":
        if score < 0.55:
            return "Medium"
        else:
            return "Low"
    elif category == "Protection Readiness":
        if score < 0.50:
            return "High"
        elif score < 0.75:
            return "Medium"
        else:
            return "Low"
    elif category == "Financial Literacy":
        if score < 0.50:
            return "High"
        elif score < 0.75:
            return "Medium"
        else:
            return "Low"
    return "Unknown"


def calculate_overall_risk(domain_risks: Dict[str, str]) -> str:
    """
    Calculate overall risk based on domain risk classifications.
    """
    counts = {"High": 0, "Medium": 0, "Low": 0}
    for risk in domain_risks.values():
        counts[risk] = counts.get(risk, 0) + 1
    
    if counts["High"] >= 2:
        return "High"
    if (counts["High"] + counts["Medium"]) >= 2:
        return "Medium"
    return "Low"


@transaction.atomic
def calculate_and_store_uhfs(user) -> Dict[str, Any]:
    """
    Calculate UHFS for the given user using new questionnaire structure.
    
    Formula: Composite = 0.25*I + 0.25*F + 0.15*R + 0.20*P + 0.15*L
    UHFS Score = ROUND(300 + composite * 600)
    
    Returns detailed breakdown with scores and risk classifications.
    """
    # Fetch all questionnaire data
    income_stability = IncomeStability.objects.filter(user=user).first()
    financial_behavior = FinancialBehavior.objects.filter(user=user).first()
    reliability_tenure = ReliabilityTenure.objects.filter(user=user).first()
    protection_readiness = ProtectionReadiness.objects.filter(user=user).first()
    literacy = UserFinancialLiteracy.objects.filter(user=user).first()
    
    # Calculate subcategory scores
    income_result = calculate_income_stability_score(income_stability)
    financial_result = calculate_financial_behavior_score(financial_behavior)
    reliability_result = calculate_reliability_tenure_score(reliability_tenure)
    protection_result = calculate_protection_readiness_score(protection_readiness)
    literacy_score = calculate_financial_literacy_score(literacy)
    
    # Extract subcategory scores
    I = income_result["subcategory_score"]
    F = financial_result["subcategory_score"]
    R = reliability_result["subcategory_score"]
    P = protection_result["subcategory_score"]
    L = literacy_score
    
    # Calculate composite score
    composite = (0.25 * I) + (0.25 * F) + (0.15 * R) + (0.20 * P) + (0.15 * L)
    composite = max(0.0, min(composite, 1.0))
    
    # Calculate UHFS score (300-900 range)
    uhfs_value = round(300 + composite * 600)
    
    # Classify risks
    domain_risks = {
        "income": classify_risk(I, "Income Stability"),
        "financial_behavior": classify_risk(F, "Financial Behavior"),
        "reliability": classify_risk(R, "Reliability & Tenure"),
        "protection": classify_risk(P, "Protection Readiness"),
        "literacy": classify_risk(L, "Financial Literacy"),
    }
    
    overall_risk = calculate_overall_risk(domain_risks)
    
    # Prepare components dict
    components_dict = {
        "I": round(I, 5),
        "F": round(F, 5),
        "R": round(R, 5),
        "P": round(P, 5),
        "L": round(L, 5),
    }
    
    # Persist UHFSScore
    score_obj, created = UHFSScore.objects.update_or_create(
        user=user,
        defaults={
            "score": int(uhfs_value),
            "components": components_dict,
            "composite": round(composite, 5),
            "domain_risk": domain_risks,
            "overall_risk": overall_risk,
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
        "domain_risk": domain_risks,
        "overall_risk": overall_risk,
        "subcategory_details": {
            "income_stability": income_result,
            "financial_behavior": financial_result,
            "reliability_tenure": reliability_result,
            "protection_readiness": protection_result,
            "literacy": {"score": L},
        },
        "saved": True,
    }
    
    return result

