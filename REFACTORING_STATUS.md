# Questionnaire Refactoring - Current Status

## ✅ Completed

1. **New Models Created:**
   - ✅ `IncomeStability` (Q12-15)
   - ✅ `FinancialBehavior` (Q16-19)
   - ✅ `ReliabilityTenure` (Q20-23)
   - ✅ `ProtectionReadiness` (Q24-27)
   - ✅ Updated `PersonalDemographic` (Q1-10)
   - ✅ Updated `IncomeEmployment` (Q11 - simplified)
   - ✅ Updated `UserFinancialLiteracy` (Q28 - added literacy_score)

2. **New UHFS Scoring Logic:**
   - ✅ Created `finance/services/uhfs_v2.py` with new scoring formulas
   - ✅ Implements all subcategory calculations with correct weights
   - ✅ Risk classification logic

3. **New Serializers:**
   - ✅ `IncomeStabilitySerializer`
   - ✅ `FinancialBehaviorSerializer`
   - ✅ `ReliabilityTenureSerializer`
   - ✅ `ProtectionReadinessSerializer`

4. **New Views:**
   - ✅ `IncomeStabilityView`
   - ✅ `FinancialBehaviorView`
   - ✅ `ReliabilityTenureView`
   - ✅ `ProtectionReadinessView`

5. **Updated:**
   - ✅ `OnboardingProgress` model with new step choices
   - ✅ `utils.py` with new QUESTIONNAIRE_STEPS
   - ✅ `UHFSScoreView` to use V2 scoring
   - ✅ Admin registrations for new models

## ⚠️ Pending (Causing Errors)

1. **Old Views Still Reference Removed Models:**
   - `BankingFinancialAccessView` - references `BankingFinancialAccess` (removed)
   - `CreditLiabilitiesView` - references `CreditLiabilities` (removed)
   - `SavingsInsuranceView` - references `SavingsInsurance` (removed)
   - `ExpensesObligationsView` - references `ExpensesObligations` (removed)
   - `BehavioralPsychometricView` - references `BehavioralPsychometric` (removed)
   - `GovernmentSchemeEligibilityView` - references `GovernmentSchemeEligibility` (removed)

2. **Old Models Need to be Removed:**
   - These models were replaced by the new consolidated structure
   - Need to create migration to drop these tables

## 🔧 Next Steps to Fix

### Step 1: Comment out old views (temporary fix)
```python
# In finance/views.py, comment out:
# - BankingFinancialAccessView
# - CreditLiabilitiesView
# - SavingsInsuranceView
# - ExpensesObligationsView
# - BehavioralPsychometricView
# - GovernmentSchemeEligibilityView
```

### Step 2: Remove old model imports from views.py
Already done - but old views still reference them

### Step 3: Create migration
```bash
python manage.py makemigrations finance
python manage.py migrate finance
```

### Step 4: Test new endpoints
- POST /api/finance/income-stability/
- POST /api/finance/financial-behavior/
- POST /api/finance/reliability-tenure/
- POST /api/finance/protection-readiness/

## 📋 New API Endpoints

All endpoints support GET, POST, PUT, PATCH:

1. **Personal & Demographic (Q1-10):**
   ```
   POST /api/finance/personal-demographic/
   ```

2. **Income & Employment (Q11):**
   ```
   POST /api/finance/income-employment/
   ```

3. **Income Stability (Q12-15):**
   ```
   POST /api/finance/income-stability/
   ```

4. **Financial Behavior (Q16-19):**
   ```
   POST /api/finance/financial-behavior/
   ```

5. **Reliability & Tenure (Q20-23):**
   ```
   POST /api/finance/reliability-tenure/
   ```

6. **Protection Readiness (Q24-27):**
   ```
   POST /api/finance/protection-readiness/
   ```

7. **UHFS Score (uses V2 logic):**
   ```
   POST /api/finance/uhfs-score/
   ```

## 🗑️ Models to Remove (After Migration)

These old models should be removed from `models.py`:
- `BankingFinancialAccess`
- `CreditLiabilities`
- `SavingsInsurance`
- `ExpensesObligations`
- `BehavioralPsychometric`
- `GovernmentSchemeEligibility`

