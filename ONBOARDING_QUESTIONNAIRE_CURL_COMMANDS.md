# Onboarding Questionnaire API - Curl Commands

This document provides curl commands for all pages of the new consolidated onboarding questionnaire structure.

**Base URL:** `http://localhost:8000/api/finance/`

**Authentication:** All endpoints require Bearer token authentication.

---

## Page 1: Personal & Demographic (Q1-10)

**Endpoint:** `POST /api/finance/personal-demographic/`

**Description:** Collects personal and demographic information (all questions on one page).

### Curl Command:

```bash
curl --location 'http://localhost:8000/api/finance/personal-demographic/' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "full_name": "Rajesh Kumar",
    "age": 32,
    "gender": "Male",
    "state": "Maharashtra",
    "city_district": "Mumbai",
    "occupation_type": "Gig worker",
    "marital_status": "Married",
    "children": "Yes",
    "dependents": 2,
    "education_level": "Graduate"
}'
```

### Field Options:

- **gender**: `"Male"`, `"Female"`, `"Other"`
- **occupation_type**: `"Gig worker"`, `"Small retailer"`, `"Farmer"`, `"Other"`
- **marital_status**: `"Married"`, `"Single"`, `"Other"`
- **children**: `"Yes"`, `"No"`, `"Daughter"`
- **education_level**: `"None"`, `"School"`, `"College"`, `"Graduate"`, `"Other"`

### Response Example:

```json
{
    "id": 1,
    "full_name": "Rajesh Kumar",
    "age": 32,
    "gender": "Male",
    "state": "Maharashtra",
    "city_district": "Mumbai",
    "occupation_type": "Gig worker",
    "marital_status": "Married",
    "children": "Yes",
    "dependents": 2,
    "education_level": "Graduate"
}
```

---

## Page 2: Income & Employment (Q11)

**Endpoint:** `POST /api/finance/income-employment/`

**Description:** Collects primary source of income information.

### Curl Command:

```bash
curl --location 'http://localhost:8000/api/finance/income-employment/' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "primary_income_source": "Swiggy"
}'
```

### Field Description:

- **primary_income_source**: Text field (e.g., "Swiggy", "Zomato", "Self-employed", "Farming", "Ola", "Uber", etc.)

### Response Example:

```json
{
    "id": 1,
    "primary_income_source": "Swiggy"
}
```

---

## Page 3: Income Stability (Q12-15)

**Endpoint:** `POST /api/finance/income-stability/`

**Description:** Collects income stability information (all questions on one page).

### Curl Command:

```bash
curl --location 'http://localhost:8000/api/finance/income-stability/' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "monthly_income": "₹20,001–30,000",
    "income_drop_frequency": "Once",
    "working_days_per_week": "5–6 days",
    "income_trend": "Stable"
}'
```

### Field Options:

- **monthly_income**: 
  - `"₹5,000–10,000"`
  - `"₹10,001–20,000"`
  - `"₹20,001–30,000"`
  - `"₹30,001–50,000"`
  - `"₹50,000+"`

- **income_drop_frequency**: 
  - `"Never"`
  - `"Once"`
  - `"Often"`
  - `"Almost every month"`

- **working_days_per_week**: 
  - `"1–2 days"`
  - `"3–4 days"`
  - `"5–6 days"`
  - `"Every day"`

- **income_trend**: 
  - `"Increased"`
  - `"Stable"`
  - `"Decreased"`

### Response Example:

```json
{
    "id": 1,
    "monthly_income": "₹20,001–30,000",
    "income_drop_frequency": "Once",
    "working_days_per_week": "5–6 days",
    "income_trend": "Stable",
    "score_a": 0.6,
    "score_b": 0.7,
    "score_c": 0.75,
    "score_d": 0.8,
    "subcategory_score": 0.7125
}
```

---

## Page 4: Financial Behavior (Q16-19)

**Endpoint:** `POST /api/finance/financial-behavior/`

**Description:** Collects financial behavior information (all questions on one page).

### Curl Command:

```bash
curl --location 'http://localhost:8000/api/finance/financial-behavior/' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "monthly_savings": "₹1,000–₹3,000",
    "saving_methods": ["Bank account", "Wallet (Paytm, GPay, etc.)"],
    "missed_payments": "No",
    "bill_payment_timeliness": "Always"
}'
```

### Field Options:

- **monthly_savings**: 
  - `"Less than ₹500"`
  - `"₹500–₹1,000"`
  - `"₹1,000–₹3,000"`
  - `"More than ₹3,000"`

- **saving_methods**: Array of strings (checkboxes - can select multiple):
  - `"Bank account"`
  - `"Wallet (Paytm, GPay, etc.)"`
  - `"Cash at home"`
  - `"Not saving currently"`

- **missed_payments**: 
  - `"Yes"`
  - `"No"`
  - `"Not applicable"`

- **bill_payment_timeliness**: 
  - `"Always"`
  - `"Mostly"`
  - `"Sometimes"`
  - `"Rarely"`

### Response Example:

```json
{
    "id": 1,
    "monthly_savings": "₹1,000–₹3,000",
    "saving_methods": ["Bank account", "Wallet (Paytm, GPay, etc.)"],
    "missed_payments": "No",
    "bill_payment_timeliness": "Always",
    "score_a": 0.8,
    "score_b": 1.0,
    "score_c": 1.0,
    "score_d": 1.0,
    "subcategory_score": 0.92
}
```

---

## Page 5: Reliability & Tenure (Q20-23)

**Endpoint:** `POST /api/finance/reliability-tenure/`

**Description:** Collects reliability and tenure information (all questions on one page).

### Curl Command:

```bash
curl --location 'http://localhost:8000/api/finance/reliability-tenure/' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "platform_tenure": "6–12 months",
    "active_days_per_week": "5–6",
    "cancellation_frequency": "Rarely",
    "customer_rating": "4"
}'
```

### Field Options:

- **platform_tenure**: 
  - `"Less than 3 months"`
  - `"3–6 months"`
  - `"6–12 months"`
  - `"More than 1 year"`

- **active_days_per_week**: 
  - `"1–2"`
  - `"3–4"`
  - `"5–6"`
  - `"7 days"`

- **cancellation_frequency**: 
  - `"Rarely"`
  - `"Sometimes"`
  - `"Often"`

- **customer_rating**: 
  - `"1"` (1 star)
  - `"2"` (2 stars)
  - `"3"` (3 stars)
  - `"4"` (4 stars)
  - `"5"` (5 stars)

### Response Example:

```json
{
    "id": 1,
    "platform_tenure": "6–12 months",
    "active_days_per_week": "5–6",
    "cancellation_frequency": "Rarely",
    "customer_rating": "4",
    "score_a": 0.75,
    "score_b": 0.75,
    "score_c": 1.0,
    "score_d": 0.9,
    "subcategory_score": 0.84
}
```

---

## Page 6: Protection Readiness (Q24-27)

**Endpoint:** `POST /api/finance/protection-readiness/`

**Description:** Collects protection readiness information (all questions on one page).

### Curl Command:

```bash
curl --location 'http://localhost:8000/api/finance/protection-readiness/' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "has_health_insurance": "Yes",
    "has_accident_life_insurance": "No",
    "emergency_expense_handling": "Within 1 week",
    "current_savings_fund": "₹1,001–5,000"
}'
```

### Field Options:

- **has_health_insurance**: 
  - `"Yes"`
  - `"No"`
  - `"Not sure"`

- **has_accident_life_insurance**: 
  - `"Yes"`
  - `"No"`
  - `"Not sure"`

- **emergency_expense_handling**: 
  - `"Immediately"`
  - `"Within 1 week"`
  - `"Within 1 month"`
  - `"Cannot manage"`

- **current_savings_fund**: 
  - `"₹0–500"`
  - `"₹501–1,000"`
  - `"₹1,001–5,000"`
  - `"₹5,000+"`

### Response Example:

```json
{
    "id": 1,
    "has_health_insurance": "Yes",
    "has_accident_life_insurance": "No",
    "emergency_expense_handling": "Within 1 week",
    "current_savings_fund": "₹1,001–5,000",
    "score_a": 1.0,
    "score_b": 0.0,
    "score_c": 0.8,
    "score_d": 0.7,
    "subcategory_score": 0.61
}
```

---

## Page 7: Financial Literacy (Q28)

**Note:** Financial Literacy is not collected via a questionnaire endpoint. It is automatically calculated based on:
- Training modules completed
- Average quiz scores from training modules

The score is updated when users complete training sections. See the Training API documentation for details.

---

## Calculate UHFS Score

**Endpoint:** `POST /api/finance/uhfs-score/`

**Description:** Calculates and stores the UHFS score based on all questionnaire responses.

### Curl Command:

```bash
curl --location 'http://localhost:8000/api/finance/uhfs-score/' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--request POST
```

### Response Example:

```json
{
    "user_id": "ae661a6b-1be4-4c5d-b571-13876308beba",
    "components": {
        "I": 0.7125,
        "F": 0.92,
        "R": 0.84,
        "P": 0.61,
        "L": 0.75
    },
    "weights": {
        "I": 0.25,
        "F": 0.25,
        "R": 0.15,
        "P": 0.20,
        "L": 0.15
    },
    "composite": 0.7625,
    "uhfs_score": 757,
    "domain_risk": {
        "income": "Low",
        "financial_behavior": "Low",
        "reliability": "Low",
        "protection": "Medium",
        "literacy": "Low"
    },
    "overall_risk": "Low",
    "subcategory_details": {
        "income_stability": {
            "score": 0.7125,
            "subcategory_score": 0.7125,
            "scores": {
                "A": 0.6,
                "B": 0.7,
                "C": 0.75,
                "D": 0.8
            }
        },
        "financial_behavior": {
            "score": 0.92,
            "subcategory_score": 0.92,
            "scores": {
                "A": 0.8,
                "B": 1.0,
                "C": 1.0,
                "D": 1.0
            }
        },
        "reliability_tenure": {
            "score": 0.84,
            "subcategory_score": 0.84,
            "scores": {
                "A": 0.75,
                "B": 0.75,
                "C": 1.0,
                "D": 0.9
            }
        },
        "protection_readiness": {
            "score": 0.61,
            "subcategory_score": 0.61,
            "scores": {
                "A": 1.0,
                "B": 0.0,
                "C": 0.8,
                "D": 0.7
            }
        },
        "literacy": {
            "score": 0.75
        }
    },
    "saved": true
}
```

---

## Get Current UHFS Score

**Endpoint:** `GET /api/finance/uhfs-score/`

**Description:** Retrieves the current UHFS score and breakdown.

### Curl Command:

```bash
curl --location 'http://localhost:8000/api/finance/uhfs-score/' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--request GET
```

---

## Get Onboarding Progress

**Endpoint:** `GET /api/finance/dashboard/`

**Description:** Get user's onboarding progress and current step.

### Curl Command:

```bash
curl --location 'http://localhost:8000/api/finance/dashboard/' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--request GET
```

---

## Notes

1. **All endpoints support GET, POST, PUT, and PATCH methods:**
   - `GET`: Retrieve current data
   - `POST`: Create new record or update if exists
   - `PUT`: Full update
   - `PATCH`: Partial update

2. **UHFS Score Calculation:**
   - Automatically triggered when you submit any questionnaire page
   - Can also be manually triggered by calling `POST /api/finance/uhfs-score/`

3. **Onboarding Progress:**
   - Progress is automatically tracked when you submit each page
   - All questions in a category must be on the same page (consolidated structure)

4. **Field Validation:**
   - All dropdown fields must match the exact values shown in the options
   - Case-sensitive for some fields
   - `saving_methods` accepts an array of strings (multiple selections allowed)

5. **Scoring:**
   - Each subcategory calculates scores automatically
   - Scores are stored in the database and returned in the response
   - UHFS score ranges from 300-900

---

## Complete Onboarding Flow Example

```bash
# Step 1: Personal & Demographic
curl --location 'http://localhost:8000/api/finance/personal-demographic/' \
--header 'Authorization: Bearer YOUR_TOKEN' \
--header 'Content-Type: application/json' \
--data '{"full_name": "Rajesh Kumar", "age": 32, "gender": "Male", "state": "Maharashtra", "city_district": "Mumbai", "occupation_type": "Gig worker", "marital_status": "Married", "children": "Yes", "dependents": 2, "education_level": "Graduate"}'

# Step 2: Income & Employment
curl --location 'http://localhost:8000/api/finance/income-employment/' \
--header 'Authorization: Bearer YOUR_TOKEN' \
--header 'Content-Type: application/json' \
--data '{"primary_income_source": "Swiggy"}'

# Step 3: Income Stability
curl --location 'http://localhost:8000/api/finance/income-stability/' \
--header 'Authorization: Bearer YOUR_TOKEN' \
--header 'Content-Type: application/json' \
--data '{"monthly_income": "₹20,001–30,000", "income_drop_frequency": "Once", "working_days_per_week": "5–6 days", "income_trend": "Stable"}'

# Step 4: Financial Behavior
curl --location 'http://localhost:8000/api/finance/financial-behavior/' \
--header 'Authorization: Bearer YOUR_TOKEN' \
--header 'Content-Type: application/json' \
--data '{"monthly_savings": "₹1,000–₹3,000", "saving_methods": ["Bank account"], "missed_payments": "No", "bill_payment_timeliness": "Always"}'

# Step 5: Reliability & Tenure
curl --location 'http://localhost:8000/api/finance/reliability-tenure/' \
--header 'Authorization: Bearer YOUR_TOKEN' \
--header 'Content-Type: application/json' \
--data '{"platform_tenure": "6–12 months", "active_days_per_week": "5–6", "cancellation_frequency": "Rarely", "customer_rating": "4"}'

# Step 6: Protection Readiness
curl --location 'http://localhost:8000/api/finance/protection-readiness/' \
--header 'Authorization: Bearer YOUR_TOKEN' \
--header 'Content-Type: application/json' \
--data '{"has_health_insurance": "Yes", "has_accident_life_insurance": "No", "emergency_expense_handling": "Within 1 week", "current_savings_fund": "₹1,001–5,000"}'

# Step 7: Calculate UHFS Score
curl --location 'http://localhost:8000/api/finance/uhfs-score/' \
--header 'Authorization: Bearer YOUR_TOKEN' \
--header 'Content-Type: application/json' \
--request POST
```

