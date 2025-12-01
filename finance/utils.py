from common.constants import QUESTIONNAIRE_STEPS
from .models import (
    PersonalDemographic, IncomeEmployment, BankingFinancialAccess,
    CreditLiabilities, SavingsInsurance, ExpensesObligations,
    BehavioralPsychometric, GovernmentSchemeEligibility, UserFinancialLiteracy
)

MODEL_MAP = {
    "personal_demographic": PersonalDemographic,
    "income_employment": IncomeEmployment,
    "banking_financial_access": BankingFinancialAccess,
    "credit_liabilities": CreditLiabilities,
    "savings_insurance": SavingsInsurance,
    "expenses_obligations": ExpensesObligations,
    "behavioral_psychometric": BehavioralPsychometric,
    "government_scheme_eligibility": GovernmentSchemeEligibility,
    "user_financial_literacy": UserFinancialLiteracy
}


from .models import OnboardingProgress


def update_progress(user, step_name):
    progress, _ = OnboardingProgress.objects.get_or_create(user=user)

    # Update current step
    progress.current_step = step_name

    step_index = QUESTIONNAIRE_STEPS.index(step_name)

    # Mark completed step
    progress.completed_step = step_name

    # Check if last step completed
    if step_index == len(QUESTIONNAIRE_STEPS) - 1:
        progress.is_completed = True
    else:
        progress.is_completed = False

    progress.save()
    return progress


def get_onboarding_progress_details(user):
    """Get detailed onboarding progress information for a user"""
    progress, _ = OnboardingProgress.objects.get_or_create(user=user)
    
    # Check which steps are actually completed by checking if data exists
    completed_steps = []
    for step in QUESTIONNAIRE_STEPS:
        model = MODEL_MAP.get(step)
        if model and model.objects.filter(user=user).exists():
            completed_steps.append(step)
    
    total_steps = len(QUESTIONNAIRE_STEPS)
    completed_count = len(completed_steps)

    # Auto-sync is_completed flag based on actual completed_count
    if total_steps > 0 and completed_count == total_steps:
        # All steps done
        progress.is_completed = True
        if completed_steps:
            progress.completed_step = completed_steps[-1]
        # No further step
        next_step = None
    else:
        # Not fully completed
        progress.is_completed = False
        if completed_steps:
            last_completed = completed_steps[-1]
            try:
                idx = QUESTIONNAIRE_STEPS.index(last_completed)
                if idx < len(QUESTIONNAIRE_STEPS) - 1:
                    next_step = QUESTIONNAIRE_STEPS[idx + 1]
                else:
                    next_step = None
            except ValueError:
                next_step = QUESTIONNAIRE_STEPS[0]
        else:
            next_step = QUESTIONNAIRE_STEPS[0] if total_steps > 0 else None

    progress.save(update_fields=["is_completed", "completed_step", "current_step"])
    
    return {
        "is_completed": progress.is_completed,
        "completed_steps": completed_steps,
        "completed_count": completed_count,
        "total_steps": total_steps,
        "next_step": next_step,
        "current_step": progress.current_step,
        "progress_percentage": round((completed_count / total_steps) * 100, 2) if total_steps > 0 else 0,
    }
