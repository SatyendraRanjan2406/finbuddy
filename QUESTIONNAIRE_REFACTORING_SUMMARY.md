# Questionnaire Refactoring Summary

## Overview
Major refactoring of the onboarding questionnaire structure to consolidate questions by category and update UHFS scoring logic.

## New Structure

### 1. Personal & Demographic (Q1-10) - One Page
- Model: `PersonalDemographic` (updated)
- Endpoint: `POST /api/finance/personal-demographic/`
- Questions: Full Name, Age, Gender, State, City/District, Occupation Type, Marital Status, Children, Dependents, Education Level

### 2. Income & Employment (Q11) - One Page
- Model: `IncomeEmployment` (simplified - only primary_income_source)
- Endpoint: `POST /api/finance/income-employment/`
- Question: Primary Source of Income

### 3. Income Stability (Q12-15) - One Page
- Model: `IncomeStability` (NEW)
- Endpoint: `POST /api/finance/income-stability/`
- Questions:
  - Q12 (A): Monthly income (weight 20%)
  - Q13 (B): Income drop frequency (weight 50%)
  - Q14 (C): Working days per week (weight 25%)
  - Q15 (D): Income trend (weight 5%)
- Formula: `0.20*A + 0.50*B + 0.25*C + 0.05*D`

### 4. Financial Behavior (Q16-19) - One Page
- Model: `FinancialBehavior` (NEW)
- Endpoint: `POST /api/finance/financial-behavior/`
- Questions:
  - Q16 (A): Monthly savings (weight 40%)
  - Q17 (B): Saving methods - checkboxes (weight 10%)
  - Q18 (C): Missed payments (weight 30%)
  - Q19 (D): Bill payment timeliness (weight 20%)
- Formula: `0.40*A + 0.10*B + 0.30*C + 0.20*D`

### 5. Reliability & Tenure (Q20-23) - One Page
- Model: `ReliabilityTenure` (NEW)
- Endpoint: `POST /api/finance/reliability-tenure/`
- Questions:
  - Q20 (A): Platform tenure (weight 40%)
  - Q21 (B): Active days per week (weight 30%)
  - Q22 (C): Cancellation frequency (weight 20%)
  - Q23 (D): Customer rating (weight 10%)
- Formula: `0.40*A + 0.30*B + 0.20*C + 0.10*D`

### 6. Protection Readiness (Q24-27) - One Page
- Model: `ProtectionReadiness` (NEW)
- Endpoint: `POST /api/finance/protection-readiness/`
- Questions:
  - Q24 (A): Health insurance (weight 30%)
  - Q25 (B): Accident/life insurance (weight 30%)
  - Q26 (C): Emergency expense handling (weight 30%)
  - Q27 (D): Current savings/emergency funds (weight 10%)
- Formula: `0.30*A + 0.30*B + 0.30*C + 0.10*D`

### 7. Financial Literacy (Q28)
- Model: `UserFinancialLiteracy` (updated - added literacy_score field)
- Based on training modules completed and quiz scores

## UHFS Scoring Formula

**Composite Score:**
```
Composite = 0.25*I + 0.25*F + 0.15*R + 0.20*P + 0.15*L
```

**Final UHFS Score:**
```
UHFS = ROUND(300 + composite * 600)
```

**Risk Classifications:**
- Income Stability: I < 0.45 (High), 0.45 ≤ I < 0.70 (Medium), I ≥ 0.70 (Low)
- Financial Behavior: F < 0.50 (High), 0.50 ≤ F < 0.75 (Medium), F ≥ 0.75 (Low)
- Reliability & Tenure: R < 0.55 (Medium), R ≥ 0.55 (Low)
- Protection Readiness: P < 0.50 (High), 0.50 ≤ P < 0.75 (Medium), P ≥ 0.75 (Low)
- Financial Literacy: L < 0.50 (High), 0.50 ≤ L < 0.75 (Medium), L ≥ 0.75 (Low)

## Models Removed
The following old models should be removed (after data migration):
- `BankingFinancialAccess`
- `CreditLiabilities`
- `SavingsInsurance`
- `ExpensesObligations`
- `BehavioralPsychometric`
- `GovernmentSchemeEligibility`

## New Files Created
1. `finance/services/uhfs_v2.py` - New UHFS scoring logic
2. New serializers for: `IncomeStability`, `FinancialBehavior`, `ReliabilityTenure`, `ProtectionReadiness`
3. New views for: `IncomeStabilityView`, `FinancialBehaviorView`, `ReliabilityTenureView`, `ProtectionReadinessView`

## Migration Steps

1. **Create migrations:**
   ```bash
   python manage.py makemigrations finance
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate finance
   ```

3. **Data Migration (if needed):**
   - Create a script to migrate data from old models to new models
   - Map old fields to new questionnaire structure

4. **Remove old views/models:**
   - Comment out or remove old view classes
   - Remove old model classes from models.py
   - Create final migration to drop old tables

## API Endpoints

### New Endpoints:
- `POST /api/finance/income-stability/` - Q12-15
- `POST /api/finance/financial-behavior/` - Q16-19
- `POST /api/finance/reliability-tenure/` - Q20-23
- `POST /api/finance/protection-readiness/` - Q24-27

### Updated Endpoints:
- `POST /api/finance/personal-demographic/` - Q1-10 (updated fields)
- `POST /api/finance/income-employment/` - Q11 (simplified)
- `POST /api/finance/uhfs-score/` - Uses new V2 scoring logic

## Next Steps

1. Fix import errors in views.py (remove old view references)
2. Create migration to add new models
3. Create data migration script (if needed)
4. Test new questionnaire flow
5. Remove old models and views
6. Update frontend to use new structure

